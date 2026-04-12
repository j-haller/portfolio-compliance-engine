"""Rule: no holdings may belong to an excluded sector."""


def check_exclusion(holdings: list[dict], rule: dict) -> dict:
    """Check that no holding belongs to the excluded target sector.

    BREACH if any holding's sector matches the rule target.
    """
    target: str = rule["target"] or ""
    breaches = [h["ticker"] for h in holdings if (h.get("sector") or "").strip() == target.strip()]

    if breaches:
        return _result(rule, "BREACH", f"Excluded sector '{target}': {', '.join(breaches)}")
    return _result(rule, "PASS", f"No exposure to excluded sector '{target}'")


def _result(rule: dict, status: str, detail: str) -> dict:
    return {"rule_id": rule["id"], "rule_name": rule["name"], "status": status, "detail": detail}
