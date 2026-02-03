# Company Tracker Database API

A FastAPI application implementing an **append-only temporal database pattern** for tracking companies, metrics, products, and market shares with full history.

## Features

- **Append-Only Temporal Pattern**: All changes are tracked with full history using `is_current` flags
- **Point-in-Time Queries**: Query data as it was at any moment in time
- **Audit Trail**: All changes include `created_by` tracking
- **No Data Deletion**: Data is never deleted, only superseded
- **RESTful API**: Full CRUD operations with proper validation

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start PostgreSQL and API
docker-compose up -d

# Check logs
docker-compose logs -f api

# API is available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env

# Start PostgreSQL (or use Docker)
docker-compose up -d db

# Run migrations
alembic upgrade head

# Seed sample data (optional)
python scripts/seed_data.py

# Start the API
uvicorn app.main:app --reload
```

## API Endpoints

### Companies

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/companies` | Upsert a company |
| GET | `/api/companies` | List all current companies |
| GET | `/api/companies/{id}` | Get current state of company |
| GET | `/api/companies/{id}/history` | Get full history |
| GET | `/api/companies/{id}/at/{date}` | Point-in-time query |

### Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/metrics` | Upsert a metric |
| GET | `/api/metrics` | List current metrics (with filters) |
| GET | `/api/companies/{id}/metrics` | Get company metrics |

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/products` | Upsert product hierarchy |
| GET | `/api/products` | List current products |
| GET | `/api/products/{id}` | Get product by class_3_id |

### Shares

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/shares` | Upsert share |
| GET | `/api/shares` | List shares (filterable) |
| GET | `/api/companies/{id}/shares` | Get company's product shares |
| GET | `/api/reports/market-share` | Aggregated market share report |

## Sample curl Commands

### Create a Company

```bash
curl -X POST http://localhost:8000/api/companies \
  -H "Content-Type: application/json" \
  -H "X-User: admin@example.com" \
  -d '{
    "company_id": 1,
    "company_name": "Novo Nordisk",
    "percentage_a": 0.25,
    "percentage_b": 0.35,
    "percentage_c": 0.40
  }'
```

### Update a Company (Creates New Version)

```bash
curl -X POST http://localhost:8000/api/companies \
  -H "Content-Type: application/json" \
  -H "X-User: admin@example.com" \
  -d '{
    "company_id": 1,
    "company_name": "Novo Nordisk A/S",
    "percentage_a": 0.30,
    "percentage_b": 0.35,
    "percentage_c": 0.35
  }'
```

### Get Company History

```bash
curl http://localhost:8000/api/companies/1/history
```

### Point-in-Time Query

```bash
curl "http://localhost:8000/api/companies/1/at/2024-06-01T00:00:00"
```

### Create Metrics

```bash
curl -X POST http://localhost:8000/api/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "country_code": "DK",
    "year": 2024,
    "revenue": 150000000.00,
    "gross_profit": 85000000.00,
    "headcount": 5200
  }'
```

### Create Product Hierarchy

```bash
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "product_class_3_id": 101,
    "class_level_1": "Medical Devices",
    "class_level_2": "Diagnostic Equipment",
    "class_level_3": "Blood Glucose Monitors"
  }'
```

### Create Product Share

```bash
curl -X POST http://localhost:8000/api/shares \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "country_code": "DK",
    "product_class_3_id": 101,
    "share_percentage": 0.3250
  }'
```

### Get Market Share Report

```bash
curl "http://localhost:8000/api/reports/market-share?country_code=DK"
```

## Database Schema

### Tables

All tables follow the append-only temporal pattern with these common columns:

| Column | Type | Description |
|--------|------|-------------|
| `record_id` | BIGSERIAL | Primary key (unique per version) |
| `valid_from` | TIMESTAMP | When this version became active |
| `valid_to` | TIMESTAMP | When this version was superseded (NULL if current) |
| `is_current` | BOOLEAN | True for the current version |
| `created_by` | VARCHAR(100) | User who created this version |

### Upsert Logic

When you POST data:

1. **New entity**: Creates a new record with `is_current=True`
2. **Changed data**: Closes old record (`is_current=False`, `valid_to=now`) and creates new record
3. **No change**: Returns existing record without creating a new version

The response includes:
- `record_id`: The record ID
- `is_new`: `true` if a new record was created, `false` if unchanged

## Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_companies.py -v
```

## Project Structure

```
company-tracker-db/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Settings from environment
│   ├── database.py          # SQLAlchemy engine/session
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic validation schemas
│   ├── repositories/        # Data access with upsert logic
│   └── routers/             # API endpoints
├── alembic/                 # Database migrations
├── tests/                   # Pytest test suite
├── scripts/                 # Utility scripts
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async database URL |
| `DATABASE_URL_SYNC` | `postgresql://...` | Sync URL (for Alembic) |
| `APP_ENV` | `development` | Environment mode |
| `DEBUG` | `true` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DEFAULT_USER` | `system` | Default created_by value |

## License

MIT
