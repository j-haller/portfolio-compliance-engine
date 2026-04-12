using Microsoft.Data.Sqlite;
using ComplianceEngine.Data;
using ComplianceEngine.Models;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);

var dbPath = Environment.GetEnvironmentVariable("DB_PATH") ?? "/db/compliance_engine.db";
builder.Services.AddSingleton(new DatabaseContext(dbPath));

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
        policy
            .WithOrigins("http://localhost:8050", "http://localhost", "http://dashboard:8050")
            .AllowAnyMethod()
            .AllowAnyHeader());
});

// Use snake_case JSON so Python clients receive field names like rule_type, portfolio_id, etc.
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
});

var app = builder.Build();
app.UseCors();

// ── Rules ──────────────────────────────────────────────────────────────────────

/// <summary>Returns compliance rules. Pass ?all=true to include inactive rules.</summary>
app.MapGet("/api/rules", (DatabaseContext db, bool? all) =>
{
    using var conn = db.CreateConnection();
    conn.Open();
    using var cmd = conn.CreateCommand();
    cmd.CommandText = all == true
        ? "SELECT id, name, rule_type, threshold, target, active FROM rule ORDER BY id"
        : "SELECT id, name, rule_type, threshold, target, active FROM rule WHERE active = 1 ORDER BY id";

    var rules = new List<Rule>();
    using var reader = cmd.ExecuteReader();
    while (reader.Read())
    {
        rules.Add(new Rule(
            reader.GetInt32(0),
            reader.GetString(1),
            reader.GetString(2),
            reader.IsDBNull(3) ? null : reader.GetDouble(3),
            reader.IsDBNull(4) ? null : reader.GetString(4),
            reader.GetInt32(5)
        ));
    }
    return Results.Ok(rules);
});

/// <summary>Creates a new compliance rule. Returns 201 with the created rule.</summary>
app.MapPost("/api/rules", (DatabaseContext db, RuleRequest req) =>
{
    if (string.IsNullOrWhiteSpace(req.Name) || string.IsNullOrWhiteSpace(req.RuleType))
        return Results.BadRequest("name and rule_type are required");

    using var conn = db.CreateConnection();
    conn.Open();
    using var cmd = conn.CreateCommand();
    cmd.CommandText = @"
        INSERT INTO rule (name, rule_type, threshold, target)
        VALUES (@name, @ruleType, @threshold, @target);
        SELECT last_insert_rowid();";
    cmd.Parameters.AddWithValue("@name", req.Name);
    cmd.Parameters.AddWithValue("@ruleType", req.RuleType);
    cmd.Parameters.AddWithValue("@threshold", req.Threshold.HasValue ? req.Threshold.Value : DBNull.Value);
    cmd.Parameters.AddWithValue("@target", req.Target ?? (object)DBNull.Value);

    var id = (long)cmd.ExecuteScalar()!;
    var created = new Rule((int)id, req.Name, req.RuleType, req.Threshold, req.Target, 1);
    return Results.Created($"/api/rules/{id}", created);
});

/// <summary>Updates a rule's fields. Set active=0 to deactivate or active=1 to reactivate.</summary>
app.MapPut("/api/rules/{id:int}", (DatabaseContext db, int id, RuleRequest req) =>
{
    using var conn = db.CreateConnection();
    conn.Open();
    using var cmd = conn.CreateCommand();
    cmd.CommandText = @"
        UPDATE rule
        SET name=@name, rule_type=@ruleType, threshold=@threshold, target=@target, active=@active
        WHERE id=@id";
    cmd.Parameters.AddWithValue("@name", req.Name);
    cmd.Parameters.AddWithValue("@ruleType", req.RuleType);
    cmd.Parameters.AddWithValue("@threshold", req.Threshold.HasValue ? req.Threshold.Value : DBNull.Value);
    cmd.Parameters.AddWithValue("@target", req.Target ?? (object)DBNull.Value);
    cmd.Parameters.AddWithValue("@active", req.Active ?? 1);
    cmd.Parameters.AddWithValue("@id", id);

    return cmd.ExecuteNonQuery() == 0 ? Results.NotFound() : Results.Ok();
});

/// <summary>Soft-deletes a rule by setting active=0.</summary>
app.MapDelete("/api/rules/{id:int}", (DatabaseContext db, int id) =>
{
    using var conn = db.CreateConnection();
    conn.Open();
    using var cmd = conn.CreateCommand();
    cmd.CommandText = "UPDATE rule SET active=0 WHERE id=@id";
    cmd.Parameters.AddWithValue("@id", id);
    return cmd.ExecuteNonQuery() == 0 ? Results.NotFound() : Results.Ok();
});

// ── Portfolios ─────────────────────────────────────────────────────────────────

/// <summary>Returns all portfolios ordered by upload date descending.</summary>
app.MapGet("/api/portfolios", (DatabaseContext db) =>
{
    using var conn = db.CreateConnection();
    conn.Open();
    using var cmd = conn.CreateCommand();
    cmd.CommandText = "SELECT id, name, uploaded_at FROM portfolio ORDER BY uploaded_at DESC";

    var portfolios = new List<Portfolio>();
    using var reader = cmd.ExecuteReader();
    while (reader.Read())
        portfolios.Add(new Portfolio(reader.GetInt32(0), reader.GetString(1), reader.GetString(2)));

    return Results.Ok(portfolios);
});

/// <summary>Returns a portfolio and all its holdings. Returns 404 if not found.</summary>
app.MapGet("/api/portfolios/{id:int}", (DatabaseContext db, int id) =>
{
    using var conn = db.CreateConnection();
    conn.Open();

    Portfolio? portfolio = null;
    using (var cmd = conn.CreateCommand())
    {
        cmd.CommandText = "SELECT id, name, uploaded_at FROM portfolio WHERE id=@id";
        cmd.Parameters.AddWithValue("@id", id);
        using var reader = cmd.ExecuteReader();
        if (reader.Read())
            portfolio = new Portfolio(reader.GetInt32(0), reader.GetString(1), reader.GetString(2));
    }
    if (portfolio is null)
        return Results.NotFound();

    var holdings = new List<Holding>();
    using (var cmd2 = conn.CreateCommand())
    {
        cmd2.CommandText = @"
            SELECT id, portfolio_id, ticker, isin, sector, country, weight
            FROM holding WHERE portfolio_id=@id";
        cmd2.Parameters.AddWithValue("@id", id);
        using var reader2 = cmd2.ExecuteReader();
        while (reader2.Read())
        {
            holdings.Add(new Holding(
                reader2.GetInt32(0), reader2.GetInt32(1), reader2.GetString(2),
                reader2.IsDBNull(3) ? null : reader2.GetString(3),
                reader2.IsDBNull(4) ? null : reader2.GetString(4),
                reader2.IsDBNull(5) ? null : reader2.GetString(5),
                reader2.GetDouble(6)
            ));
        }
    }

    return Results.Ok(portfolio with { Holdings = holdings });
});

/// <summary>Saves a new portfolio with its holdings. Returns 201 with the new portfolio ID.</summary>
app.MapPost("/api/portfolios", (DatabaseContext db, PortfolioRequest req) =>
{
    if (string.IsNullOrWhiteSpace(req.Name))
        return Results.BadRequest("name is required");
    if (req.Holdings is null || req.Holdings.Count == 0)
        return Results.BadRequest("at least one holding is required");

    using var conn = db.CreateConnection();
    conn.Open();
    using var tx = conn.BeginTransaction();

    long portfolioId;
    using (var cmd = conn.CreateCommand())
    {
        cmd.Transaction = tx;
        cmd.CommandText = "INSERT INTO portfolio (name) VALUES (@name); SELECT last_insert_rowid();";
        cmd.Parameters.AddWithValue("@name", req.Name);
        portfolioId = (long)cmd.ExecuteScalar()!;
    }

    foreach (var h in req.Holdings)
    {
        using var hcmd = conn.CreateCommand();
        hcmd.Transaction = tx;
        hcmd.CommandText = @"
            INSERT INTO holding (portfolio_id, ticker, isin, sector, country, weight)
            VALUES (@pid, @ticker, @isin, @sector, @country, @weight)";
        hcmd.Parameters.AddWithValue("@pid", portfolioId);
        hcmd.Parameters.AddWithValue("@ticker", h.Ticker);
        hcmd.Parameters.AddWithValue("@isin", h.Isin ?? (object)DBNull.Value);
        hcmd.Parameters.AddWithValue("@sector", h.Sector ?? (object)DBNull.Value);
        hcmd.Parameters.AddWithValue("@country", h.Country ?? (object)DBNull.Value);
        hcmd.Parameters.AddWithValue("@weight", h.Weight);
        hcmd.ExecuteNonQuery();
    }

    tx.Commit();
    return Results.Created($"/api/portfolios/{portfolioId}", new { id = portfolioId });
});

app.Run();

// ── Request DTOs ───────────────────────────────────────────────────────────────

record RuleRequest(string Name, string RuleType, double? Threshold, string? Target, int? Active = 1);
record HoldingRequest(string Ticker, string? Isin, string? Sector, string? Country, double Weight);
record PortfolioRequest(string Name, List<HoldingRequest> Holdings);
