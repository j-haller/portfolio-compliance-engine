"""Page 1 — Upload a portfolio CSV and trigger a compliance check."""

import base64
import csv
import io
import os

import dash
import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, State, callback, dcc, html

dash.register_page(__name__, path="/", title="Upload Portfolio — Portfolio Compliance Engine")

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5050")


def layout() -> html.Div:
    """Upload page layout."""
    return dbc.Container(
        [
            html.H2("Upload Portfolio", className="mb-4"),
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Label("Portfolio Name", html_for="portfolio-name"),
                        dbc.Input(
                            id="portfolio-name",
                            placeholder="e.g. Q1 2024 Global Portfolio",
                            type="text",
                            className="mb-3",
                        ),
                    ],
                    md=6,
                )
            ),
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Label("Portfolio CSV"),
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div(
                                ["Drag & Drop or ", html.A("Select CSV File")],
                                style={"lineHeight": "80px"},
                            ),
                            style={
                                "width": "100%",
                                "height": "80px",
                                "borderWidth": "2px",
                                "borderStyle": "dashed",
                                "borderRadius": "8px",
                                "textAlign": "center",
                                "cursor": "pointer",
                                "background": "#f8f9fa",
                            },
                            multiple=False,
                        ),
                        html.Div(id="file-info", className="mt-2 text-muted small"),
                    ],
                    md=8,
                ),
                className="mb-3",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Button(
                        "Run Compliance Check",
                        id="submit-btn",
                        color="primary",
                        size="lg",
                        disabled=True,
                    )
                ),
                className="mb-3",
            ),
            html.Div(id="upload-status"),
            dcc.Location(id="upload-redirect"),
        ],
        className="px-4",
    )


@callback(
    Output("file-info", "children"),
    Output("submit-btn", "disabled"),
    Input("upload-data", "filename"),
)
def on_file_selected(filename: str | None) -> tuple:
    """Show selected filename and enable the submit button."""
    if filename:
        return f"Selected: {filename}", False
    return "", True


@callback(
    Output("upload-redirect", "href"),
    Output("upload-status", "children"),
    Input("submit-btn", "n_clicks"),
    State("portfolio-name", "value"),
    State("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def submit_portfolio(
    _n_clicks: int,
    name: str | None,
    contents: str | None,
    _filename: str | None,
) -> tuple:
    """Parse the uploaded CSV and POST the portfolio to the C# API."""
    if not name or not name.strip():
        return dash.no_update, dbc.Alert("Please enter a portfolio name.", color="warning")
    if not contents:
        return dash.no_update, dbc.Alert("Please upload a CSV file.", color="warning")

    try:
        _content_type, content_string = contents.split(",", 1)
        decoded = base64.b64decode(content_string).decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))
        holdings = []
        for row in reader:
            holdings.append(
                {
                    "ticker": row["ticker"].strip(),
                    "isin": row.get("isin", "").strip() or None,
                    "sector": row.get("sector", "").strip() or None,
                    "country": row.get("country", "").strip() or None,
                    "weight": float(row["weight"].strip()),
                }
            )
    except Exception as exc:
        return dash.no_update, dbc.Alert(f"CSV parse error: {exc}", color="danger")

    if not holdings:
        return dash.no_update, dbc.Alert("CSV contains no holdings.", color="warning")

    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/portfolios",
            json={"name": name.strip(), "holdings": holdings},
            timeout=10,
        )
        resp.raise_for_status()
        portfolio_id = resp.json()["id"]
        return f"/results/{portfolio_id}", None
    except Exception as exc:
        return dash.no_update, dbc.Alert(f"Error saving portfolio: {exc}", color="danger")
