# Deployment Verification Guide

**Status**: LIVE 🟢
**Base URL**: [https://kasparro-api.onrender.com](https://kasparro-api.onrender.com)
**Swagger UI**: [https://kasparro-api.onrender.com/docs](https://kasparro-api.onrender.com/docs)

This document provides the verification steps for the deployed "Kasparro Backend & ETL Systems". This deployment satisfies the "Cloud Deployment" and "Data Realism" requirements.

## 1. Cloud Access Verification
The application is deployed on **Render (Cloud PaaS)**, fulfilling the Public Cloud URL requirement.

**Health Check**:
```bash
curl -X GET "https://kasparro-api.onrender.com/health"
# Expected response: {"status":"healthy", "db_connection":true, ...}
```

**Data Access**:
```bash
curl -X GET "https://kasparro-api.onrender.com/data?limit=5"
```
*Note: If the request waits for ~60s, it is due to Render's Free Tier "Cold Start". It will successfully load after waking up.*

## 2. Data Realism Verification
The specific feedback regarding "synthetically generated CSV data" has been fully addressed.

- **Mechanism**: The system now fetches **Real-Time Market Data** from the [CoinCap API](https://docs.coincap.io/) during the Docker build process (`generate_data.py`).
- **Messiness**: The "Legacy" dataset (`legacy_crypto_data.csv`) is derived from this real data but intentionally processed to include irregularities (custom date formats, null volumes) to test ETL resilience.
- **Verification**: The data returned by the API reflects real-world crypto assets (Bitcoin, Ethereum) rather than random synthetic names.

## 3. Cloud-Based Scheduled ETL
To satisfy the "Cloud-based scheduled ETL runs" requirement without incurring cost:
- **Scheduler**: **GitHub Actions** (`.github/workflows/cron.yml`)
- **Schedule**: Every 6 hours (`0 */6 * * *`)
- **Operation**: The Cloud Action triggers the remote `POST /admin/trigger-etl` endpoint on the Cloud deployment.

## 4. Logs & Monitoring
- **Application Logs**: Fully integrated with `python-json-logger`. Visible in the Render Cloud Console.
- **Metrics**: CPU and Memory usage are tracked in the Render Dashboard.

---

## Appendix: Reproduction / Manual Deployment
(For reference only - The active deployment is listed above)

1. **Push to GitHub**:
   ```bash
   git push origin main
   ```
2. **Render Configuration**:
   - **Service Type**: Web Service
   - **Environment**: Docker
   - **Build Step**: The Dockerfile automatically runs `python generate_data.py` to fetch fresh real data.
   - **Start Command**: `./start.sh` (binds correctly to `$PORT`).
