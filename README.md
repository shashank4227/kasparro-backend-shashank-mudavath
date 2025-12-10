# Kasparro Backend Assignment - P0 Foundation Layer

This project implements a production-grade ETL pipeline and Backend API for cryptocurrency data, fully Dockerized and ready for cloud deployment.

## Features (Verification Checklist)
- **Data Ingestion**: Fetches from CoinGecko, CoinPaprika, and CSV files (Legacy/Normal).
- **Normalization**: Unified `crypto_market_data` schema in PostgreSQL.
- **API**: FastAPI service with Pagination, Filtering (`source`), and Health checks.
- **Resilience**: Implements rate limiting, retries w/ exponential backoff, and failure recovery.
- **Security**: fully configured for environment-based secrets (no hardcoded keys).

## 🚀 Quick Start (Evaluators)

### 1. Run with Docker
The system runs universally via Docker Compose.
```bash
# Provide API Keys (Optional - defaults to free tier)
export COINGECKO_API_KEY="your_key"
export COINPAPRIKA_API_KEY="your_key"

make up
# Or: docker-compose up --build -d
```
> **Note**: The API starts **immediately** (`start.sh` runs ETL in background).

### 2. Verify API & Smoke Test
Run the automated smoke test script to verify End-to-End functionality:
```bash
# Requires python requests
python smoke_test.py
```
Or manually:
- Health: [http://localhost:8000/health](http://localhost:8000/health)
- Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run Test Suite
Executes all 22 automated tests covering ETL, Recovery, Drift, and API.
```bash
make test
```

## ☁️ Cloud Deployment
The system is designed for deployment on **Render** (or AWS/GCP).
> **[View Cloud Deployment Guide](deployment_guide.md)**
> Only a browser is required to verify the deployment instructions.

## 🛡️ Security & Configuration
- **API Keys**: Injected via `COINGECKO_API_KEY` and `COINPAPRIKA_API_KEY` environment variables.
- **Database**: Configured via `POSTGRES_*` variables in `docker-compose.yml`.

## 🧪 Testing Coverage
| Type | Coverage |
| :--- | :--- |
| **ETL** | Schema validation, Pydantic models |
| **Recovery** | Checkpointing, resume-after-crash logic |
| **Drift** | Fuzzy matching for schema changes (e.g. `price` -> `prce`) |
| **Resilience** | Rate limiter delays, ConnectionError handling |

## Assignment Notes
- **ETL on Boot**: Configured in `start.sh` to run in background for immediate API availability.
- **CSV Data**: `crypto_data.csv` and `legacy_crypto_data.csv` are baked into the image.

