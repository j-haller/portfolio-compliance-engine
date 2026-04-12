"""Compliance engine: fetches portfolio + rules from API, runs all active rules."""

import requests

from rules.exclusion import check_exclusion
from rules.max_country_weight import check_max_country_weight
from rules.max_weight import check_max_weight
from rules.min_diversification import check_min_diversification
from rules.min_holdings import check_min_holdings

_RULE_CHECKERS = {
    "max_weight": check_max_weight,
    "exclusion": check_exclusion,
    "min_diversification": check_min_diversification,
    "max_country_weight": check_max_country_weight,
    "min_holdings": check_min_holdings,
}


def run_compliance_check(portfolio_id: int, api_base_url: str) -> list[dict]:
    """Fetch portfolio and active rules from the API, run every rule, return results.

    Args:
        portfolio_id: ID of the portfolio to check.
        api_base_url: Base URL of the C# API (e.g. "http://api:5050").

    Returns:
        List of result dicts, one per active rule:
        [{"rule_id": int, "rule_name": str, "status": "PASS"|"WARN"|"BREACH", "detail": str}, ...]
    """
    portfolio = _fetch_portfolio(portfolio_id, api_base_url)
    holdings: list[dict] = portfolio.get("holdings", [])
    rules: list[dict] = _fetch_rules(api_base_url)

    results: list[dict] = []
    for rule in rules:
        checker = _RULE_CHECKERS.get(rule["rule_type"])
        if checker is None:
            results.append({
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "status": "PASS",
                "detail": f"Rule type '{rule['rule_type']}' not implemented — skipped",
            })
            continue
        results.append(checker(holdings, rule))

    return results


def _fetch_portfolio(portfolio_id: int, api_base_url: str) -> dict:
    """Fetch a portfolio with its holdings from the API."""
    url = f"{api_base_url}/api/portfolios/{portfolio_id}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _fetch_rules(api_base_url: str) -> list[dict]:
    """Fetch all active compliance rules from the API."""
    url = f"{api_base_url}/api/rules"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()
