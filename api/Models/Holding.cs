namespace ComplianceEngine.Models;

/// <summary>A single holding within a portfolio.</summary>
public record Holding(
    int Id,
    int PortfolioId,
    string Ticker,
    string? Isin,
    string? Sector,
    string? Country,
    double Weight
);
