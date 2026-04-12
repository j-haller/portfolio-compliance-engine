"""Rule: top-10 holdings combined weight must not exceed a threshold."""


def check_min_diversification(holdings: list[dict], rule: dict) -> dict:
    """Check concentration risk using the top-10 holdings by weight.

    BREACH if top-10 combined weight > threshold.
    WARN   if top-10 combined weight > threshold * 0.9.
    """
    threshold: float = rule["threshold"]
    top10 = sorted(holdings, key=lambda h: h["weight"], reverse=True)[:10]
    combined = sum(h["weight"] for h in top10)

    if combined > threshold:
        return _result(rule, "BREACH", f"Top-10 combined: {combined * 100:.1f}% (limit: {threshold * 100:.0f}%)")
    if combined > threshold * 0.9:
        return _result(rule, "WARN", f"Top-10 combined: {combined * 100:.1f}% (limit: {threshold * 100:.0f}%)")
    return _result(rule, "PASS", f"Top-10 combined: {combined * 100:.1f}% (limit: {threshold * 100:.0f}%)")


def _result(rule: dict, status: str, detail: str) -> dict:
    return {"rule_id": rule["id"], "rule_name": rule["name"], "status": status, "detail": detail}
