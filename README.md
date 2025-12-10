# Kasparro Backend Assignment - P0 Foundation Layer

This project implements a production-grade ETL pipeline and Backend API for cryptocurrency data.

## Features
- **Data Ingestion**: Fetches from CoinGecko API and CSV files.
- **Normalization**: Unified schema in PostgreSQL.
- **Validation**: Pydantic models for type safety.
- **API**: FastAPI service with Pagination, Filtering, and Health checks.
- **Containerization**: Fully Dockerized.

## Prerequisites
- Docker & Docker Compose
- Make (optional, commands available in Makefile)

## Quick Start

### 1. Run the System
To start the database and the backend service (which runs ETL on boot):
```bash
make up
```
*Alternatively: `docker-compose up --build -d`*

### 2. Verify
Check the health status:
```bash
curl http://localhost:8000/health
```

Query data:
```bash
curl "http://localhost:8000/data?limit=5"
```

### 3. Run Tests
```bash
make test
```

### 4. Stop System
```bash
make down
```

## Design Decisions
- **FastAPI**: Chosen for async performance and native Pydantic support.
- **ETL on Boot**: For this assignment, `start.sh` runs the ETL script before starting the API server. In a high-scale production system, this would be a separate CronJob or Airflow DAG.
- **PostgreSQL**: Used for robust relational data storage.
- **Docker**: Ensures consistent environment across dev and prod.
