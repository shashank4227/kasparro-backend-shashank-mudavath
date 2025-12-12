# Cloud Deployment Guide to Render (Recommended)

This guide walks through deploying the Kasparro ETL Backend to **Render.com** which offers a free tier for both web services and PostgreSQL databases, satisfying the requirement for public APIs and cloud accessibility.

## Prerequisites
- A [GitHub account](https://github.com/) (to host your code)
- A [Render account](https://render.com/)

---

## Step 1: Push Code to GitHub
1. Create a new public/private repository on GitHub.
2. Push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit with real data fetch"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/kasparro-backend.git
   git push -u origin main
   ```

## Step 2: Create a Cloud Database
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **PostgreSQL**.
3. Name it `kasparro-db`.
4. Choose the **Free** tier.
5. Once created, copy the **Internal Connection String** (for use within Render) and **External Connection String** (for connecting from your laptop).

## Step 3: Deploy the Web Service
1. On Render, click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure:
   - **Name**: `kasparro-api`
   - **Environment**: `Docker`
   - **Region**: Any
   - **Instance Type**: Free
4. **Environment Variables**:
   Add the following variables:
   - `DATABASE_URL`: *Paste the Internal Connection String from Step 2*
   - `COINGECKO_API_KEY`: *Your Key (Optional)*
   - `COINPAPRIKA_API_KEY`: *Your Key (Optional)*
   - `PYTHONUNBUFFERED`: `1`
   - `PORT`: `8000` (Optional, Render sets this automatically)
5. Click **Create Web Service**.

> [!IMPORTANT]
> Render will automatically run `docker build`.
> **During the build setup defined in `Dockerfile`, the system will execute `python generate_data.py` to fetch REAL crypto data from CoinCap API.**
> This ensures your deployment contains realistic, messy market data as required.

## Step 4: CRITICAL - Verify Deployment
**You MUST verify the deployment is accessible.**

1. Wait for the deploy to finish. Render will show "Live" and provide a URL like `https://kasparro-api-abcd.onrender.com`.
2. **COPY THIS URL.**
3. Open your browser and visit: `https://YOUR-APP-URL.onrender.com/docs`
   - You should see the Swagger UI.
4. **Required for Submission**:
   - Ensure you include this **ACTUAL** URL in your submission form.
   - Do NOT submit `https://kasparro-api.onrender.com` (that is a placeholder).

Test via terminal:
```bash
# Replace with your ACTUAL URL
curl https://kasparro-api-abcd.onrender.com/health
```

## Step 5: Scheduled ETL Run (Free Option)
Render's native "Cron Job" service is paid. To satisfy the "Cloud-based scheduled ETL" requirement for **free**, use **GitHub Actions**.

### 1. Enable ETL Trigger Endpoint
 The backend has a `POST /admin/trigger-etl` endpoint.

### 2. Set up GitHub Action Cron
Create ` .github/workflows/cron.yml` (already provided in repo):
```yaml
name: Scheduled ETL Trigger
on:
  schedule:
    - cron: '0 */6 * * *'  # Runs every 6 hours
  workflow_dispatch:       # Allows manual trigger button
jobs:
  trigger-etl:
    runs-on: ubuntu-latest
    steps:
      - name: Call API Endpoint
        run: |
          # REPLACE WITH YOUR ACTUAL RENDER URL
          curl -X POST https://kasparro-api-abcd.onrender.com/admin/trigger-etl \
            -H "Content-Type: application/json"
```

## Step 6: Logs & Monitoring
- **Logs**: Visible directly in the Render Dashboard "Logs" tab.

---

# Data Persistence Note
The `crypto_data.csv` files are generated **at build time** inside the Docker image using `generate_data.py`. This satisfies the requirement for "Data Realism" by fetching live market data snapshots during deployment.
