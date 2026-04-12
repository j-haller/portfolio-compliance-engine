"""Page 2 — Compliance results for an uploaded portfolio."""

import os

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import requests
from dash import dcc, html
from engine import run_compliance_check

from components.breach_table import make_breach_table

dash.register_page(__name__, path_template="/results/<portfolio_id>", title="Results — Portfolio Compliance Engine")

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5050")


def _summary_cards(results: list[dict]) -> dbc.Row:
    """Build traffic-light summary metric cards."""
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    warns = sum(1 for r in results if r["status"] == "WARN")
    breaches = sum(1 for r in results if r["status"] == "BREACH")

    def _card(value: int, label: str, color: str, inverse: bool = False) -> dbc.Col:
        return dbc.Col(
            dbc.Card(
                dbc.CardBody([html.H3(str(value), className="mb-0"), html.P(label, className="mb-0")]),
                color=color,
                inverse=inverse,
                className="text-center",
            ),
            md=3,
        )

    return dbc.Row(
        [
            _card(total, "Total Rules", "light"),
            _card(passed, "Passed", "success", inverse=True),
            _card(warns, "Warnings", "warning", inverse=True),
            _card(breaches, "Breaches", "danger", inverse=True),
        ],
        className="mb-4 g-3",
    )


def _weight_chart(holdings: list[dict], max_weight_threshold: float | None) -> go.Figure:
    """Bar chart of portfolio holdings with optional max-weight reference line."""
    sorted_h = sorted(holdings, key=lambda h: h["weight"], reverse=True)
    tickers = [h["ticker"] for h in sorted_h]
    weights = [round(h["weight"] * 100, 2) for h in sorted_h]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=tickers,
            y=weights,
            marker_color="steelblue",
            hovertemplate="%{x}: %{y:.2f}%<extra></extra>",
        )
    )

    if max_weight_threshold is not None:
        fig.add_hline(
            y=max_weight_threshold * 100,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"Max weight limit ({max_weight_threshold * 100:.0f}%)",
            annotation_position="top right",
        )

    fig.update_layout(
        xaxis_title="Ticker",
        yaxis_title="Weight (%)",
        height=380,
        margin={"t": 20, "b": 40},
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#e5e5e5")
    return fig


def layout(portfolio_id: str | None = None, **_kwargs) -> html.Div:
    """Results page: run compliance check and render report."""
    if portfolio_id is None:
        return dbc.Alert("No portfolio ID provided.", color="warning")

    try:
        results = run_compliance_check(int(portfolio_id), API_BASE_URL)
    except Exception as exc:
        return dbc.Alert(f"Compliance engine error: {exc}", color="danger")

    try:
        port_resp = requests.get(f"{API_BASE_URL}/api/portfolios/{portfolio_id}", timeout=10)
        port_resp.raise_for_status()
        portfolio = port_resp.json()
        holdings: list[dict] = portfolio.get("holdings", [])
        portfolio_name: str = portfolio.get("name", f"Portfolio {portfolio_id}")
    except Exception:
        holdings = []
        portfolio_name = f"Portfolio {portfolio_id}"

    # Find the first max_weight threshold to draw the reference line on the chart
    max_weight_threshold: float | None = None
    try:
        rules_resp = requests.get(f"{API_BASE_URL}/api/rules", timeout=10)
        for rule in rules_resp.json():
            if rule["rule_type"] == "max_weight" and rule.get("threshold") is not None:
                max_weight_threshold = rule["threshold"]
                break
    except Exception:
        pass

    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(f"Compliance Report: {portfolio_name}", className="mb-1"),
                            html.P(f"Portfolio ID: {portfolio_id}", className="text-muted small"),
                        ],
                        md=9,
                    ),
                    dbc.Col(
                        dbc.Button("← Upload New", href="/", color="outline-secondary"),
                        md=3,
                        className="d-flex align-items-center justify-content-end",
                    ),
                ],
                className="mb-3",
            ),
            _summary_cards(results),
            html.H4("Rule Results", className="mb-3"),
            make_breach_table(results),
            html.H4("Portfolio Weights", className="mt-4 mb-2"),
            dcc.Graph(figure=_weight_chart(holdings, max_weight_threshold), config={"displayModeBar": False}),
        ],
        className="px-4",
    )
