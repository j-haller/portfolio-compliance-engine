"""Portfolio Compliance Engine — Dash application entry point."""

import sys

# Engine is mounted at /engine in the container; add to path before pages are imported.
sys.path.insert(0, "/engine")

import dash
import dash_bootstrap_components as dbc
from dash import html

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

server = app.server

app.layout = dbc.Container(
    [
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Upload", href="/")),
                dbc.NavItem(dbc.NavLink("Rules", href="/rules")),
            ],
            brand="Portfolio Compliance Engine",
            brand_href="/",
            color="primary",
            dark=True,
            className="mb-0",
        ),
        html.Div(style={"height": "24px"}),
        dash.page_container,
    ],
    fluid=True,
    style={"padding": "0"},
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True, use_reloader=False)
    # use_reloader=False — watchfiles handles restarting on file changes
