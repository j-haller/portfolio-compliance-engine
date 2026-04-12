using Microsoft.Data.Sqlite;

namespace ComplianceEngine.Data;

/// <summary>Provides SQLite connections using the configured DB path.</summary>
public class DatabaseContext
{
    private readonly string _connectionString;

    public DatabaseContext(string dbPath)
    {
        _connectionString = $"Data Source={dbPath}";
    }

    /// <summary>Opens and returns a new SQLite connection.</summary>
    public SqliteConnection CreateConnection() => new SqliteConnection(_connectionString);
}
