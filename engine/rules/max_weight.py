"""Rule: no single holding may exceed a weight threshold."""


def check_max_weight(holdings: list[dict], rule: dict) -> dict:
    """Check that no single holding exceeds the configured weight threshold.

    BREACH if any holding weight > threshold.
    WARN   if any holding weight > threshold * 0.9 (within 10% of limit).
    """
    threshold: float = rule["threshold"]
    warn_threshold = threshold * 0.9

    breaches = [(h["ticker"], h["weight"]) for h in holdings if h["weight"] > threshold]
    if breaches:
        detail = ", ".join(f"{t}: {w * 100:.1f}%" for t, w in breaches)
        return _result(rule, "BREACH", detail)

    warns = [(h["ticker"], h["weight"]) for h in holdings if h["weight"] > warn_threshold]
    if warns:
        detail = ", ".join(f"{t}: {w * 100:.1f}%" for t, w in warns)
        return _result(rule, "WARN", detail)

    max_w = max(h["weight"] for h in holdings) if holdings else 0.0
    return _result(rule, "PASS", f"Max holding: {max_w * 100:.1f}% (limit: {threshold * 100:.0f}%)")


def _result(rule: dict, status: str, detail: str) -> dict:
    return {"rule_id": rule["id"], "rule_name": rule["name"], "status": status, "detail": detail}
