"""Page 3 — Manage compliance rules: view, add, toggle active/inactive."""

import os

import dash
import dash_bootstrap_components as dbc
import requests
from dash import ALL, Input, Output, State, callback, ctx, dcc, html

dash.register_page(__name__, path="/rules", title="Rule Manager — Portfolio Compliance Engine")

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5050")

RULE_TYPES = [
    "max_weight",
    "exclusion",
    "min_diversification",
    "max_country_weight",
    "min_holdings",
]


def _fetch_rules(include_all: bool = True) -> list[dict]:
    """Fetch rules from the C# API."""
    try:
        url = f"{API_BASE_URL}/api/rules" + ("?all=true" if include_all else "")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def _make_rules_table(rules: list[dict]) -> dbc.Table:
    """Build the rules table from a list of rule dicts."""
    rows = []
    for rule in rules:
        active = rule["active"] == 1
        threshold = rule.get("threshold")
        threshold_str = f"{threshold * 100:.0f}%" if threshold is not None else "—"
        rows.append(
            html.Tr(
                [
                    html.Td(rule["id"], className="text-muted"),
                    html.Td(rule["name"]),
                    html.Td(dbc.Badge(rule["rule_type"], color="info", text_color="dark")),
                    html.Td(threshold_str),
                    html.Td(rule.get("target") or "—"),
                    html.Td(
                        dbc.Badge("Active", color="success")
                        if active
                        else dbc.Badge("Inactive", color="secondary")
                    ),
                    html.Td(
                        dbc.Button(
                            "Deactivate" if active else "Activate",
                            id={"type": "toggle-btn", "index": rule["id"]},
                            color="outline-warning" if active else "outline-success",
                            size="sm",
                        )
                    ),
                ]
            )
        )

    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("ID"),
                        html.Th("Name"),
                        html.Th("Type"),
                        html.Th("Threshold"),
                        html.Th("Target"),
                        html.Th("Status"),
                        html.Th("Action"),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        bordered=True,
        hover=True,
        striped=True,
        responsive=True,
    )


def layout() -> html.Div:
    """Rule manager page layout."""
    rules = _fetch_rules()
    return dbc.Container(
        [
            html.H2("Rule Manager", className="mb-4"),
            dcc.Store(id="rules-store", data=rules),
            html.Div(id="rules-table-container", children=_make_rules_table(rules)),
            # ── Add Rule Form ────────────────────────────────────────────────────
            dbc.Card(
                [
                    dbc.CardHeader(html.H5("Add New Rule", className="mb-0")),
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Label("Name"),
                                            dbc.Input(id="new-rule-name", placeholder="e.g. No Energy sector"),
                                        ],
                                        md=4,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Type"),
                                            dbc.Select(
                                                id="new-rule-type",
                                                options=[{"label": t, "value": t} for t in RULE_TYPES],
                                                value=RULE_TYPES[0],
                                            ),
                                        ],
                                        md=3,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Threshold"),
                                            dbc.Input(
                                                id="new-rule-threshold",
                                                placeholder="e.g. 0.10",
                                                type="number",
                                                min=0,
                                                step=0.01,
                                            ),
                                        ],
                                        md=2,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Label("Target (sector/ticker)"),
                                            dbc.Input(id="new-rule-target", placeholder="e.g. Energy"),
                                        ],
                                        md=3,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.Button("Add Rule", id="add-rule-btn", color="primary"),
                        ]
                    ),
                ],
                className="mt-4",
            ),
            html.Div(id="add-rule-status", className="mt-3"),
        ],
        className="px-4",
    )


@callback(
    Output("rules-store", "data"),
    Output("rules-table-container", "children"),
    Output("add-rule-status", "children"),
    Input("add-rule-btn", "n_clicks"),
    Input({"type": "toggle-btn", "index": ALL}, "n_clicks"),
    State("rules-store", "data"),
    State("new-rule-name", "value"),
    State("new-rule-type", "value"),
    State("new-rule-threshold", "value"),
    State("new-rule-target", "value"),
    prevent_initial_call=True,
)
def mutate_rules(
    _add_clicks: int | None,
    _toggle_clicks: list,
    rules_data: list[dict],
    name: str | None,
    rule_type: str | None,
    threshold: float | None,
    target: str | None,
) -> tuple:
    """Handle add-rule and toggle-active actions."""
    triggered = ctx.triggered_id
    status_msg = None

    if triggered == "add-rule-btn":
        if not name or not name.strip():
            status_msg = dbc.Alert("Rule name is required.", color="warning")
        else:
            try:
                payload = {
                    "name": name.strip(),
                    "rule_type": rule_type,
                    "threshold": float(threshold) if threshold is not None else None,
                    "target": target.strip() if target else None,
                }
                resp = requests.post(f"{API_BASE_URL}/api/rules", json=payload, timeout=10)
                resp.raise_for_status()
                status_msg = dbc.Alert("Rule added.", color="success", duration=3000)
            except Exception as exc:
                status_msg = dbc.Alert(f"Error adding rule: {exc}", color="danger")

    elif isinstance(triggered, dict) and triggered.get("type") == "toggle-btn":
        rule_id = triggered["index"]
        current = next((r for r in (rules_data or []) if r["id"] == rule_id), None)
        if current:
            new_active = 0 if current["active"] == 1 else 1
            try:
                if new_active == 0:
                    requests.delete(f"{API_BASE_URL}/api/rules/{rule_id}", timeout=10)
                else:
                    payload = {
                        "name": current["name"],
                        "rule_type": current["rule_type"],
                        "threshold": current.get("threshold"),
                        "target": current.get("target"),
                        "active": 1,
                    }
                    requests.put(f"{API_BASE_URL}/api/rules/{rule_id}", json=payload, timeout=10)
            except Exception as exc:
                status_msg = dbc.Alert(f"Error toggling rule: {exc}", color="danger")

    new_rules = _fetch_rules()
    return new_rules, _make_rules_table(new_rules), status_msg
