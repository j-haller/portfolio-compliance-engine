# portguard — Claude Code Instructions

## Project Overview
Portfolio compliance rule engine for asset management.
Upload a portfolio CSV → check it against compliance rules → get a traffic-light breach report.

Built to demonstrate skills for a software engineering role.

---

## Stack
| Layer | Technology |
|---|---|
| Frontend | Python + Plotly Dash |
| Rule Engine | Python |
| REST API | C# ASP.NET Core (minimal API) |
| Database | SQLite (via SQL) |
| Reverse Proxy | nginx |
| Containerization | Docker + Docker Compose |
| Hot Reload (Python) | watchfiles |
| Hot Reload (C#) | dotnet watch |

---

## Repository Structure
```
portguard/
├── CLAUDE.md
├── README.md
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
├── api/                        # C# ASP.NET Core minimal API
│   ├── Dockerfile
│   ├── portguard.csproj
│   ├── Program.cs
│   ├── Models/
│   │   ├── Rule.cs
│   │   ├── Portfolio.cs
│   │   └── Holding.cs
│   └── Data/
│       └── DatabaseContext.cs
├── engine/                     # Python rule engine
│   ├── requirements.txt
│   ├── rules/
│   │   ├── __init__.py
│   │   ├── max_weight.py
│   │   ├── exclusion.py
│   │   └── min_diversification.py
│   └── engine.py
├── dashboard/                  # Plotly Dash frontend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   ├── pages/
│   │   ├── upload.py
│   │   ├── results.py
│   │   └── rule_manager.py
│   └── components/
│       └── breach_table.py
├── db/
│   ├── schema.sql
│   └── seed.sql
└── data/
    └── sample_portfolio.csv
```

---

## Database Schema

Three tables in SQLite:

```sql
-- Compliance rules
CREATE TABLE rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rule_type TEXT NOT NULL,   -- "max_weight" | "exclusion" | "min_diversification"
    threshold REAL,            -- e.g. 0.10 for 10%
    target TEXT,               -- sector name or ticker, NULL if not applicable
    active INTEGER DEFAULT 1
);

-- Uploaded portfolios
CREATE TABLE portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    uploaded_at TEXT DEFAULT (datetime('now'))
);

-- Holdings per portfolio
CREATE TABLE holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER REFERENCES portfolios(id),
    ticker TEXT NOT NULL,
    isin TEXT,
    sector TEXT,
    country TEXT,
    weight REAL NOT NULL       -- decimal, e.g. 0.05 = 5%
);
```

Seed with at least 5 realistic rules and 1 sample portfolio.

---

## C# API (api/)

ASP.NET Core minimal API. No controllers — use `app.MapGet` / `app.MapPost` style.

### Endpoints
```
GET  /api/rules              → return all active rules as JSON
POST /api/rules              → create a new rule (JSON body)
PUT  /api/rules/{id}         → update a rule
DELETE /api/rules/{id}       → soft-delete (set active=0)
GET  /api/portfolios         → list all portfolios
GET  /api/portfolios/{id}    → return portfolio + holdings as JSON
POST /api/portfolios         → save a new portfolio + holdings
```

### Requirements
- Use Microsoft.Data.Sqlite for DB access (raw SQL, no Entity Framework)
- Return proper HTTP status codes (200, 201, 400, 404)
- CORS enabled for localhost (Dash runs on port 8050)
- Run on port 5050

---

## Python Rule Engine (engine/)

`engine.py` exposes a single function:

```python
def run_compliance_check(portfolio_id: int, api_base_url: str) -> list[dict]:
    """
    Fetches portfolio and rules from C# API.
    Runs all active rules.
    Returns list of results:
    [
        {
            "rule_id": 1,
            "rule_name": "Max single stock weight",
            "status": "BREACH",   # "PASS" | "WARN" | "BREACH"
            "detail": "AAPL: 14.2%",
        },
        ...
    ]
    """
```

### Rule types to implement

1. **max_weight**: No single holding may exceed `threshold` (e.g. 10%).
   - BREACH if any holding > threshold
   - WARN if any holding > threshold * 0.9

2. **exclusion**: No holding in a given `target` sector allowed.
   - BREACH if any holding matches sector

3. **min_diversification**: Top-N holdings combined weight must be < `threshold`.
   - Use top 10 holdings. BREACH if combined > threshold. WARN if > threshold * 0.9.

Each rule type lives in its own file under `rules/`.

---

## Plotly Dash Frontend (dashboard/)

Three pages using `dash.page_container`:

### Page 1: Upload (`/`)
- Drag & drop CSV upload (`dcc.Upload`)
- CSV format: `ticker, isin, sector, country, weight`
- Portfolio name input field
- On submit: POST to C# API to save, then redirect to results

### Page 2: Results (`/results/<portfolio_id>`)
- Call Python engine to run compliance check
- Show summary: total rules, passed, warnings, breaches (metric cards)
- Breach table with columns: Rule | Status (colored badge) | Detail
- Color coding: 🔴 BREACH = red, 🟡 WARN = yellow, 🟢 PASS = green
- Bar chart: portfolio weights, with a horizontal line at the max_weight threshold

### Page 3: Rule Manager (`/rules`)
- Table of all rules fetched from C# API
- Button to add new rule (opens a form: name, type, threshold, target)
- Toggle active/inactive per rule

---

## Sample Portfolio CSV (data/sample_portfolio.csv)
```
ticker,isin,sector,country,weight
AAPL,US0378331005,Technology,USA,0.142
MSFT,US5949181045,Technology,USA,0.098
NESN,CH0012221716,Consumer Staples,Switzerland,0.075
NOVN,CH0012221716,Healthcare,Switzerland,0.063
BALN,CH0012221716,Tobacco,Switzerland,0.031
ROG,CH0012221716,Healthcare,Switzerland,0.058
GOOGL,US02079K3059,Technology,USA,0.089
AMZN,US0231351067,Consumer Discretionary,USA,0.072
JPM,US46625H1005,Financials,USA,0.045
BLK,US09248X1081,Financials,USA,0.038
SHEL,GB00BP6MXD84,Energy,UK,0.041
ASML,NL0010273215,Technology,Netherlands,0.055
LVMH,FR0000121014,Consumer Discretionary,France,0.049
MC,FR0000121014,Consumer Discretionary,France,0.044
SAN,ES0113900J37,Financials,Spain,0.036
UBSG,CH0244767585,Financials,Switzerland,0.065
```

---

## Seed Rules (db/seed.sql)
Include at least:
1. Max single stock weight: 10% threshold
2. No tobacco sector exposure
3. Top-10 concentration < 60%
4. No single country > 50% weight
5. Min number of holdings >= 10

---

## Docker Setup

Everything runs via Docker Compose. The single command to start the full stack is:

```bash
docker compose up
```

The app is then accessible at **http://localhost** (port 80, served by nginx).

---

## docker-compose.yml

Define four services: `nginx`, `dashboard`, `api`, `db-init`.

```yaml
services:

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - dashboard
      - api

  dashboard:
    build: ./dashboard
    volumes:
      - ./dashboard:/app          # mount source for hot reload
      - ./db:/db
      - ./data:/data
    environment:
      - API_BASE_URL=http://api:5050
      - DB_PATH=/db/portguard.db
    depends_on:
      - api

  api:
    build: ./api
    volumes:
      - ./api:/app                # mount source for hot reload
      - ./db:/db
    environment:
      - DB_PATH=/db/portguard.db
      - ASPNETCORE_URLS=http://+:5050

  db-init:
    image: keinos/sqlite3
    volumes:
      - ./db:/db
    command: >
      sh -c "sqlite3 /db/portguard.db < /db/schema.sql &&
             sqlite3 /db/portguard.db < /db/seed.sql"
    # Runs once on startup to initialize the database
```

---

## nginx/nginx.conf

nginx acts as a reverse proxy:
- `/api/` → forwards to C# API on port 5050
- `/` → forwards to Dash on port 8050

```nginx
events {}

http {
  server {
    listen 80;

    location /api/ {
      proxy_pass http://api:5050/api/;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
      proxy_pass http://dashboard:8050/;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      # Required for Dash websocket (hot reload)
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
    }
  }
}
```

---

## dashboard/Dockerfile

Use `watchfiles` to hot-reload the Dash app on file changes.
Do NOT use `CMD ["python", "app.py"]` — use watchfiles instead.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source is mounted as a volume — do not COPY it
CMD ["watchfiles", "--filter", "python", "python app.py"]
```

Add `watchfiles` to `dashboard/requirements.txt`.

Configure Dash for hot reload in `app.py`:
```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True, use_reloader=False)
    # use_reloader=False because watchfiles handles restarting
```

---

## api/Dockerfile

Use `dotnet watch` for hot reload on C# source changes.

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0

WORKDIR /app

COPY *.csproj .
RUN dotnet restore

# Source is mounted as a volume — do not COPY it
ENV DOTNET_USE_POLLING_FILE_WATCHER=1
CMD ["dotnet", "watch", "run", "--no-hot-reload"]
```

`DOTNET_USE_POLLING_FILE_WATCHER=1` is required for file watching to work inside Docker volumes.
`--no-hot-reload` forces a full restart on change (safer for minimal APIs).

---

## Service Ports (internal)
| Service | Internal Port | Exposed via |
|---|---|---|
| nginx | 80 | localhost:80 (direct) |
| dashboard | 8050 | nginx proxy at `/` |
| api | 5050 | nginx proxy at `/api/` |

No service ports other than nginx should be exposed to the host in docker-compose.yml.

---

## Dev Setup

```bash
# First time only — builds images
docker compose build

# Start everything (with hot reload)
docker compose up

# Rebuild a single service after Dockerfile change
docker compose up --build dashboard
```

Changes to Python files in `dashboard/` and C# files in `api/` are picked up automatically without restarting Docker.

---

## Code Quality Requirements
- Python: type hints on all functions, docstrings on public functions
- C#: XML doc comments on all endpoints
- No hardcoded paths or ports — use environment variables everywhere
- README.md must explain architecture, setup steps, and stack choices

---

## Out of Scope (do not build)
- Authentication / login
- Multi-user support
- Real market data integration
- Production hardening (TLS, resource limits, etc.)
