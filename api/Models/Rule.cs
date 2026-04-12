namespace ComplianceEngine.Models;

/// <summary>A compliance rule that can be applied to a portfolio.</summary>
public record Rule(
    int Id,
    string Name,
    string RuleType,
    double? Threshold,
    string? Target,
    int Active
);
