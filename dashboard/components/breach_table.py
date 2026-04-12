"""Reusable breach table component."""

import dash_bootstrap_components as dbc
from dash import html

_STATUS_COLOR = {"PASS": "success", "WARN": "warning", "BREACH": "danger"}


def make_breach_table(results: list[dict]) -> dbc.Table:
    """Build a styled table from compliance check results.

    Args:
        results: List of result dicts from run_compliance_check.

    Returns:
        A Bootstrap-styled Dash table component.
    """
    rows = [
        html.Tr([
            html.Td(r["rule_name"]),
            html.Td(
                dbc.Badge(
                    r["status"],
                    color=_STATUS_COLOR.get(r["status"], "secondary"),
                    className="fs-6 px-3 py-1",
                )
            ),
            html.Td(r["detail"]),
        ])
        for r in results
    ]

    return dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Rule"), html.Th("Status"), html.Th("Detail")])),
            html.Tbody(rows),
        ],
        bordered=True,
        hover=True,
        striped=True,
        responsive=True,
    )
