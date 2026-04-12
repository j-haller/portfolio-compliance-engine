"""Rule: portfolio must contain a minimum number of distinct holdings."""


def check_min_holdings(holdings: list[dict], rule: dict) -> dict:
    """Check that the portfolio has at least threshold distinct holdings.

    BREACH if count < threshold.
    """
    min_count = int(rule["threshold"])
    count = len(holdings)

    if count < min_count:
        return _result(rule, "BREACH", f"{count} holdings (minimum required: {min_count})")
    return _result(rule, "PASS", f"{count} holdings (minimum required: {min_count})")


def _result(rule: dict, status: str, detail: str) -> dict:
    return {"rule_id": rule["id"], "rule_name": rule["name"], "status": status, "detail": detail}
