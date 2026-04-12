"""Rule: no single country may exceed a combined weight threshold."""

from collections import defaultdict


def check_max_country_weight(holdings: list[dict], rule: dict) -> dict:
    """Check that no single country's total weight exceeds the threshold.

    BREACH if any country combined weight > threshold.
    WARN   if any country combined weight > threshold * 0.9.
    """
    threshold: float = rule["threshold"]
    warn_threshold = threshold * 0.9

    country_weights: dict[str, float] = defaultdict(float)
    for h in holdings:
        country = (h.get("country") or "Unknown").strip()
        country_weights[country] += h["weight"]

    breaches = [(c, w) for c, w in country_weights.items() if w > threshold]
    if breaches:
        detail = ", ".join(f"{c}: {w * 100:.1f}%" for c, w in sorted(breaches, key=lambda x: -x[1]))
        return _result(rule, "BREACH", detail)

    warns = [(c, w) for c, w in country_weights.items() if w > warn_threshold]
    if warns:
        detail = ", ".join(f"{c}: {w * 100:.1f}%" for c, w in sorted(warns, key=lambda x: -x[1]))
        return _result(rule, "WARN", detail)

    top = max(country_weights.items(), key=lambda x: x[1], default=("—", 0.0))
    return _result(rule, "PASS", f"Max country: {top[0]} {top[1] * 100:.1f}% (limit: {threshold * 100:.0f}%)")


def _result(rule: dict, status: str, detail: str) -> dict:
    return {"rule_id": rule["id"], "rule_name": rule["name"], "status": status, "detail": detail}
