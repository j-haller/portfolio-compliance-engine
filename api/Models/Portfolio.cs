namespace ComplianceEngine.Models;

/// <summary>An uploaded portfolio, optionally with its holdings.</summary>
public record Portfolio(
    int Id,
    string Name,
    string UploadedAt,
    List<Holding>? Holdings = null
);
