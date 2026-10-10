# Personal Expense Tracker (SpendWise)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.7+-E92063.svg?style=flat&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg?style=flat)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-42%20Passed-brightgreen.svg?style=flat&logo=pytest&logoColor=white)](https://pytest.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A production-grade, full-stack personal finance application powered by a **FastAPI** REST backend and a sleek, zero-dependency **SpendWise** responsive web dashboard. Built with strict data validation (**Pydantic v2**), high-performance ORM (**SQLAlchemy 2.0**), flexible database persistence (**SQLite & PostgreSQL**), and complete automated test coverage (**42 Pytest suites**).

---

## Table of Contents

- [Key Features](#key-features)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [SpendWise Web Dashboard](#spendwise-web-dashboard)
- [Project Structure](#project-structure)
- [Quickstart Guide](#quickstart-guide)
  - [Prerequisites](#prerequisites)
  - [Local Installation](#local-installation)
  - [Running the Application](#running-the-application)
- [API Reference](#api-reference)
  - [Endpoints Overview](#endpoints-overview)
  - [Request & Response Payloads](#request--response-payloads)
  - [Query Parameters & Filtering](#query-parameters--filtering)
  - [Error Handling](#error-handling)
- [Configuration & Environment Variables](#configuration--environment-variables)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Deployment & Containerization](#deployment--containerization)
  - [Docker & Docker Compose](#docker--docker-compose)
  - [Deploying to Cloud (Render / Railway)](#deploying-to-cloud-render--railway)
  - [Switching to PostgreSQL](#switching-to-postgresql)
- [License](#license)

---

## Key Features

### ⚡ High-Performance REST API
- **Full CRUD Management**: Create, list, retrieve, update, and delete expenses with automatic ID and timestamp provisioning.
- **Dynamic Query Filtering**: Filter expenses by category (case-insensitive) and custom date ranges (`start_date`, `end_date`).
- **Deep Analytics Engine**: Real-time aggregation of total expenses, category-wise spending distributions (sorted highest-first), and historical monthly summaries.
- **Fail-Safe Validation**: Pydantic v2 validation enforcing non-zero positive amounts, ISO 8601 calendar dates, trimmed non-empty strings, and safe note lengths.
- **Structured Error Responses**: Consistent JSON error schemas for bad input (`400`), not found (`404`), and validation failures (`422`) with zero internal stack trace leakage.

### 🎨 Built-in Single-Page Web App ("SpendWise")
- **Live Dashboard**: Instant visual metrics for total spend, transaction volume, top expense category, and current month's budget.
- **Category Breakdown**: Proportional progress bars displaying expense percentages across categories.
- **Monthly Explorer**: On-demand calendar query tool for any year and month.
- **Interactive Ledger**: Searchable, filterable expense table with instant client-side search, category filter, date filters, and inline actions.
- **Dark & Light Mode**: Built-in modern theme switcher with local storage persistence.
- **Multi-Currency Support**: Defaults to Indian Rupees (`₹`) with Indian number system formatting (`en-IN`), with instant switching to USD (`$`), EUR (`€`), and GBP (`£`).

### 🛠️ Production Ready
- **Dual Database Support**: SQLite for instant, zero-setup local development; production-ready PostgreSQL connection pooling for cloud deployments.
- **Interactive Documentation**: OpenAPI/Swagger UI at `/docs` and ReDoc at `/redoc`.
- **Automated CI/CD**: GitHub Actions workflow testing every pull request and push on Python 3.12.
- **Containerized**: Production-hardened `Dockerfile` (non-root `appuser`, healthcheck) and `docker-compose.yml`.

---

## Architecture & Tech Stack

```
┌────────────────────────────────────────────────────────┐
│                   Clients & Frontends                  │
│   Web Browser (SpendWise)  │  Swagger UI  │  cURL / SDK │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON
┌───────────────────────────▼────────────────────────────┐
│                    FastAPI Application                 │
│  ├── CORS Middleware                                   │
│  ├── Validation Handler (Pydantic v2)                  │
│  ├── Static Files Mount (/static -> index, css, js)    │
│  └── Routers                                           │
│       ├── /expenses (CRUD & Filters)                   │
│       ├── /summary  (Totals, Categories, Monthly)      │
│       └── /health   (Health Check)                     │
└───────────────────────────┬────────────────────────────┘
                            │ Session Injection (get_db)
┌───────────────────────────▼────────────────────────────┐
│                 SQLAlchemy 2.0 ORM Engine              │
│                 Connection Pooling & Models            │
└───────────────────────────┬────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
        SQLite (Local)             PostgreSQL (Cloud)
       `./expenses.db`            `postgresql://...`
```

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) | Modern, high-performance async-capable Python web framework |
| **Server** | [Uvicorn](https://www.uvicorn.org/) | Lightning-fast ASGI server implementation |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | Strict data parsing and model validation |
| **Database ORM** | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | Modern ORM with clean declarative mapping and connection pooling |
| **Storage** | [SQLite](https://sqlite.org/) / [PostgreSQL](https://www.postgresql.org/) | File-based development DB & scalable production relational DB |
| **Frontend UI** | HTML5, Vanilla CSS, Modern JS | Ultra-lightweight, zero-build Single Page Application |
| **Testing** | [Pytest](https://pytest.org/) & `TestClient` | 42 unit and integration tests with isolated DB fixtures |
| **Container** | Docker & Docker Compose | Multi-stage slim container deployment |

---

## SpendWise Web Dashboard

The application bundles an out-of-the-box frontend located in the `/static` directory and served directly by FastAPI.

- **URL**: Navigate to `http://localhost:8000/app` (or simply `http://localhost:8000` in your web browser).
- **Zero Build Tools Needed**: Built entirely with clean semantic HTML, modular CSS, and vanilla ES6 JavaScript—no `npm install`, Node.js, or complex compilation required.
- **Connected Directly to REST API**: Performs asynchronous `fetch()` calls against the local `/expenses` and `/summary` endpoints with live reactive state updates.

---

## Project Structure

```
Personal Expense Tracker/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI workflow (Python 3.12, Pytest)
├── app/
│   ├── __init__.py
│   ├── config.py               # Pydantic-based settings & env variable parsing
│   ├── database.py             # SQLAlchemy engine, session maker, get_db dependency
│   ├── main.py                 # FastAPI application, CORS, static routes, error handlers
│   ├── models.py               # SQLAlchemy declarative models (Expense table)
│   ├── schemas.py              # Pydantic schemas (ExpenseCreate, ExpenseResponse, etc.)
│   └── routers/
│       ├── __init__.py
│       ├── expenses.py         # POST, GET, PUT, DELETE /expenses
│       └── summary.py          # GET /summary, /summary/category, /summary/monthly
├── static/
│   ├── index.html              # SpendWise Single Page Application layout
│   ├── style.css               # Clean styling, CSS variables, dark/light theme
│   └── app.js                  # Frontend reactive state, API calls, and chart logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures & isolated test database engine
│   └── test_api.py             # 42 automated unit and integration tests
├── .dockerignore
├── .env.example                # Reference environment configuration
├── .gitignore
├── Dockerfile                  # Secure, production-ready container image
├── docker-compose.yml          # Local orchestration (App + persistent volume / Postgres)
├── Procfile                    # Web process descriptor for PaaS (Heroku / Render)
├── pytest.ini                  # Pytest configuration and path resolution
├── render.yaml                 # Infrastructure blueprint for 1-click Render deployment
└── requirements.txt            # Pinned runtime and testing dependencies
```

---

## Quickstart Guide

### Prerequisites
- **Python 3.10+** (tested up to Python 3.14)
- **pip** (Python package manager)
- *Optional*: Docker & Docker Compose (for containerized execution)

---

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/personal-expense-tracker.git
   cd personal-expense-tracker
   ```

2. **Create and activate a virtual environment:**

   - **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

   - **Windows (Command Prompt):**
     ```cmd
     python -m venv .venv
     .\.venv\Scripts\activate.bat
     ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

### Running the Application

Launch the development server with auto-reload:

```bash
uvicorn app.main:app --reload
```

Once started, explore the application interfaces:

| Interface | URL | Description |
| :--- | :--- | :--- |
| **SpendWise Web Dashboard** | [http://localhost:8000/app](http://localhost:8000/app) | Full interactive visual dashboard |
| **Interactive API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive OpenAPI testing console |
| **ReDoc Documentation** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Clean, readable API technical reference |
| **Health Check** | [http://localhost:8000/health](http://localhost:8000/health) | Uptime and readiness monitor |

> **Note**: On first boot, an SQLite database file `expenses.db` is automatically created in the project root. Your data persists across server restarts.

---

## API Reference

### Endpoints Overview

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service health status check | `200 OK` |
| `POST` | `/expenses` | Create a new expense record | `201 Created` |
| `GET` | `/expenses` | List all expenses with optional filters | `200 OK` |
| `GET` | `/expenses/{id}` | Retrieve a specific expense by ID | `200 OK` / `404 Not Found` |
| `PUT` | `/expenses/{id}` | Replace/update an existing expense | `200 OK` / `404 Not Found` |
| `DELETE` | `/expenses/{id}` | Remove an expense by ID | `200 OK` / `404 Not Found` |
| `GET` | `/summary` | Retrieve overall spend and expense count | `200 OK` |
| `GET` | `/summary/category` | Totals grouped by category (highest first) | `200 OK` |
| `GET` | `/summary/monthly` | Query total spend for a given month & year | `200 OK` / `422 Unprocessable` |

---

### Request & Response Payloads

#### 1. Create an Expense (`POST /expenses`)

**Request:**
```bash
curl -X POST http://localhost:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Groceries",
    "amount": 45.50,
    "category": "Food",
    "date": "2026-10-01",
    "note": "Weekly market restock"
  }'
```

**Response (`201 Created`):**
```json
{
  "id": 1,
  "title": "Groceries",
  "amount": 45.5,
  "category": "Food",
  "date": "2026-10-01",
  "note": "Weekly market restock",
  "created_at": "2026-10-10T18:40:46.508960"
}
```

#### 2. Update an Expense (`PUT /expenses/{id}`)

**Request:**
```bash
curl -X PUT http://localhost:8000/expenses/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Groceries Organic",
    "amount": 52.00,
    "category": "Food",
    "date": "2026-10-01",
    "note": "Included fresh produce"
  }'
```

#### 3. Category Breakdown (`GET /summary/category`)

**Response (`200 OK`):**
```json
{
  "total_amount": 165.5,
  "total_count": 2,
  "categories": [
    {
      "category": "Travel",
      "total_amount": 120.0,
      "count": 1
    },
    {
      "category": "Food",
      "total_amount": 45.5,
      "count": 1
    }
  ]
}
```

#### 4. Monthly Spending Query (`GET /summary/monthly?year=2026&month=10`)

**Response (`200 OK`):**
```json
{
  "year": 2026,
  "month": 10,
  "total_amount": 165.5,
  "total_count": 2
}
```

---

### Query Parameters & Filtering

#### Filtering `GET /expenses`
All query parameters are optional and can be seamlessly combined:

| Parameter | Type | Format | Example | Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `category` | string | Free text | `Food` | Case-insensitive exact match |
| `start_date` | string | `YYYY-MM-DD` | `2026-10-01` | Returns expenses on or after date |
| `end_date` | string | `YYYY-MM-DD` | `2026-10-31` | Returns expenses on or before date |

```bash
# Example: Filter Food expenses during October 2026
curl "http://localhost:8000/expenses?category=Food&start_date=2026-10-01&end_date=2026-10-31"
```

> **Validation Rule**: If `start_date` is later than `end_date`, the API returns `400 Bad Request`.

---

### Error Handling

Every error response follows a predictable, structured JSON contract:

```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "body.amount",
      "message": "Input should be greater than 0"
    }
  ]
}
```

| HTTP Status | Trigger Condition |
| :--- | :--- |
| `400 Bad Request` | Logical filter errors (e.g., `start_date > end_date`) |
| `404 Not Found` | Requested expense ID does not exist in the database |
| `422 Unprocessable` | Schema validation error (negative amount, invalid date format, missing required fields) |
| `500 Server Error` | Unexpected runtime failures (logged to console; details kept secure) |

---

## Configuration & Environment Variables

The application is configured using environment variables with sensible defaults. Copy `.env.example` to `.env` to customize:

```bash
cp .env.example .env
```

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Deployment environment (`development`, `staging`, `production`) |
| `HOST` | `0.0.0.0` | Network interface to bind to |
| `PORT` | `8000` | Port on which the API listens |
| `DATABASE_URL` | `sqlite:///./expenses.db` | SQLAlchemy connection string (supports SQLite and PostgreSQL) |
| `CORS_ORIGINS` | `*` | Comma-separated list of permitted origins, or `*` for all |
| `DOCS_ENABLED` | `true` | Set to `false` in production to disable `/docs` and `/redoc` |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |

---

## Testing & Quality Assurance

The codebase includes a comprehensive automated test suite built with **Pytest** and FastAPI's **TestClient**.

### Running the Tests

Ensure your virtual environment is active, then execute:

```bash
pytest -v
```

### Test Coverage Highlights (42 Tests)
- ✅ **Full CRUD Flow**: Creation, ID assignment, exact field retrieval, full replacement, and deletion.
- ✅ **Input Validation**: Rejection of `amount <= 0`, `NaN`, `Infinity`, non-ISO dates, missing fields, and whitespace-only titles/categories.
- ✅ **Query Filters**: Testing category case-insensitivity, single-boundary dates, dual-boundary dates, and date order validation (`start_date > end_date` returns 400).
- ✅ **Analytics Aggregation**: Testing zero-state summaries, single/multiple category spending totals, and monthly filters with leap years and empty months.
- ✅ **Database Isolation**: Fixtures create an isolated temporary SQLite database for each test session, guaranteeing tests never touch or mutate your actual `expenses.db`.

---

## Deployment & Containerization

### Docker & Docker Compose

A multi-stage, security-hardened `Dockerfile` is included (non-root execution, dynamic port binding, and health checks).

#### Option 1: Run with Docker CLI
```bash
# Build the Docker image
docker build -t expense-tracker .

# Run with persistent volume for SQLite
docker run -d \
  --name expense-tracker-app \
  -p 8000:8000 \
  -v expense_data:/app/data \
  -e DATABASE_URL=sqlite:////app/data/expenses.db \
  expense-tracker
```

#### Option 2: Run with Docker Compose
```bash
docker compose up --build -d
```
The service will be live at `http://localhost:8000` with data stored safely in the named volume `expense_data`.

---

### Deploying to Cloud (Render / Railway)

#### Deploy to Render
This repository includes a [`render.yaml`](render.yaml) blueprint:
1. Push your code to GitHub.
2. Sign in to [Render](https://render.com) and click **New + > Blueprint**.
3. Select your repository. Render automatically configures the web service, health check endpoint (`/health`), and start command.

#### Deploy to Railway / Heroku
The included [`Procfile`](Procfile) specifies the web worker command:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
Railway and Heroku will automatically detect the Python environment and launch the app without additional configuration.

---

### Switching to PostgreSQL

To switch from SQLite to PostgreSQL for high-concurrency production deployments:

1. Provide your PostgreSQL URI in the `DATABASE_URL` environment variable:
   ```bash
   DATABASE_URL=postgresql://username:password@db-host:5432/database_name
   ```
2. The application includes `psycopg2-binary` and automatically handles legacy `postgres://` prefixes required by modern SQLAlchemy 2.0.
3. Tables and schemas are automatically created on startup via the application lifespan hook.

---

## License

This project is licensed under the **MIT License**. Feel free to use, modify, and distribute it for personal and commercial projects.
