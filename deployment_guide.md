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
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/kasparro-backend.git
   git push -u origin main
   ```

## Step 2: Create a Cloud Database
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **PostgreSQL**.
3. Name it `kasparro-db`.
4. Choose the **Free** tier (or lowest paid for better performance).
5. Once created, copy the **Internal Connection String** (for use within Render) and **External Connection String** (for connecting from your laptop).

## Step 3: Deploy the Web Service
1. On Render, click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure:
   - **Name**: `kasparro-api`
   - **Environment**: `Docker`
   - **Instance Type**: Free
4. **Environment Variables** (Advanced):
   Add the following variables:
   - `DATABASE_URL`: *Paste the Internal Connection String from Step 2*
   - `COINGECKO_API_KEY`: *Your Key*
   - `COINPAPRIKA_API_KEY`: *Your Key*
   - `PYTHONUNBUFFERED`: `1`
5. Click **Create Web Service**.

Render will effectively run `docker build` and start your `start.sh` script automatically.

## Step 4: Verify Deployment
Once the deploy finishes, Render provides a public URL (e.g., `https://kasparro-api.onrender.com`).
Test it:
```bash
curl https://kasparro-api.onrender.com/health
```

## Step 5: Scheduled ETL Run (Free Option)
Render's native "Cron Job" service is paid. To satisfy the "Cloud-based scheduled ETL" requirement for **free**, we will use **GitHub Actions**.

### 1. Enable ETL Trigger Endpoint (Already Done)
The updated backend now has a `POST /admin/trigger-etl` endpoint.

### 2. Set up GitHub Action Cron
Create a file in your repository: `.github/workflows/cron.yml`
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
          curl -X POST https://kasparro-api.onrender.com/admin/trigger-etl \
            -H "Content-Type: application/json"
```
*(Replace `https://kasparro-api.onrender.com` with your actual Render URL)*

This setup delegates the scheduling to GitHub (which is reliable and free), ensuring your ETL runs periodically without needing a paid cloud scheduler.


## Step 6: Logs & Monitoring
- **Logs**: Visible directly in the Render Dashboard "Logs" tab for both the Web Service and Cron Job.
- **Metrics**: Render provides basic CPU/RAM metrics in the dashboard.

---

# Data Persistence Note
The `crypto_data.csv` files inside the docker image are "static" if deployed this way. For a real production app, you would upload CSVs to AWS S3 / Google Cloud Storage and have the script download them. For this assignment, packaging them in the Docker image is acceptable as "local" files.
