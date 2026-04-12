# Portfolio Compliance Engine

Portfolio compliance rule engine for asset management.

Upload a portfolio CSV → check it against configurable compliance rules → get a traffic-light breach report.

Built as a technical demonstration for a software engineering role.

---

## Architecture

```
browser
  │
  ▼
nginx (port 80)  ── /api/* ──▶  C# ASP.NET Core API (port 5050)
  │                                      │
  └── /* ──▶  Plotly Dash (port 8050)    │
                    │                    │
                    ├── calls API ───────┘
                    └── runs Python rule engine
```

| Layer         | Technology                        |
|---------------|-----------------------------------|
| Frontend      | Python + Plotly Dash              |
| Rule Engine   | Python                            |
| REST API      | C# ASP.NET Core (minimal API)     |
| Database      | SQLite                            |
| Reverse Proxy | nginx                             |
| Containers    | Docker + Docker Compose           |
| Hot Reload    | watchfiles (Python), dotnet watch |

All services communicate over Docker's internal network. Only nginx is exposed to the host.

---

## Quick Start

```bash
# Clone and enter the project
git clone <repo-url>
cd portfolio-compliance-engine

# Build images and start the stack (first run takes a few minutes)
docker compose up --build

# On subsequent runs
docker compose up
```

Open **http://localhost** in your browser.

The sample portfolio (16 holdings) and 5 seed rules are loaded automatically on first run.

---

## Usage

### Upload page (`/`)
1. Enter a portfolio name.
2. Drag & drop or select a CSV file with columns: `ticker, isin, sector, country, weight`.
3. Click **Run Compliance Check** — you'll be redirected to the results page.

### Results page (`/results/<id>`)
- Traffic-light summary cards (Passed / Warnings / Breaches).
- Detailed rule-by-rule table with status badges.
- Bar chart of all holdings with a max-weight reference line.

### Rule Manager (`/rules`)
- View all compliance rules and their status.
- Add a new rule via the form.
- Deactivate / reactivate individual rules.

---

## Rule Types

| Type                | Description                                          | Threshold | Target  |
|---------------------|------------------------------------------------------|-----------|---------|
| `max_weight`        | No single holding may exceed this weight             | e.g. 0.10 | —       |
| `exclusion`         | No holding in the given sector allowed               | —         | sector  |
| `min_diversification` | Top-10 combined weight must be below threshold     | e.g. 0.60 | —       |
| `max_country_weight`| No single country may exceed this total weight       | e.g. 0.50 | —       |
| `min_holdings`      | Portfolio must contain at least this many holdings   | e.g. 10   | —       |

Each rule produces one of three statuses:

- **PASS** — rule satisfied
- **WARN** — within 10% of the limit (where applicable)
- **BREACH** — rule violated

---

## CSV Format

```
ticker,isin,sector,country,weight
AAPL,US0378331005,Technology,USA,0.142
MSFT,US5949181045,Technology,USA,0.098
...
```

`weight` is a decimal (0.10 = 10%). A sample file is at `data/sample_portfolio.csv`.

---

## API Reference

All endpoints are prefixed with `/api/` and served via nginx.

| Method   | Path                    | Description                          |
|----------|-------------------------|--------------------------------------|
| GET      | `/api/rules`            | List active rules (`?all=true` for all) |
| POST     | `/api/rules`            | Create a rule                        |
| PUT      | `/api/rules/{id}`       | Update a rule (incl. active flag)    |
| DELETE   | `/api/rules/{id}`       | Soft-delete (set active=0)           |
| GET      | `/api/portfolios`       | List all portfolios                  |
| GET      | `/api/portfolios/{id}`  | Get portfolio + holdings             |
| POST     | `/api/portfolios`       | Upload a new portfolio               |

JSON uses `snake_case` field names throughout.

---

## Development

Changes to Python files under `dashboard/` and C# files under `api/` are picked up
automatically without restarting Docker (watchfiles / dotnet watch).

```bash
# Rebuild after changing a Dockerfile
docker compose up --build dashboard
docker compose up --build api

# View logs for a single service
docker compose logs -f dashboard
docker compose logs -f api
```

---

## Stack Rationale

- **Plotly Dash** — rapid Python UI development, built-in reactive callbacks, no JavaScript needed.
- **ASP.NET Core minimal API** — lightweight, fast, modern C# without controller boilerplate.
- **SQLite** — zero-config embedded database; sufficient for a single-user demo.
- **Docker Compose** — one command to start the full stack; reproducible across machines.
- **nginx** — single entry point, clean URL routing, WebSocket support for Dash hot-reload.

---

## Out of Scope

- Authentication / user management
- Real market data feeds
- Production hardening (TLS, resource limits, secrets management)
