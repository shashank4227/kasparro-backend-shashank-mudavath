import csv
import requests
import random
from datetime import datetime
import time

def fetch_real_data():
    """Fetch top 100 assets from CoinCap API (free, no key needed)."""
    url = "https://api.coincap.io/v2/assets"
    try:
        response = requests.get(url, params={"limit": 100})
        response.raise_for_status()
        return response.json()["data"]
    except Exception as e:
        print(f"Error fetching data from CoinCap: {e}")
        return []

def generate_csv(filename="crypto_data.csv"):
    headers = ["symbol", "price", "volume", "timestamp", "source"]
    data = []
    
    assets = fetch_real_data()
    if not assets:
        print("Using fallback synthetic data due to API failure.")
        # Fallback to avoid empty file if API is down
        return generate_synthetic_csv(filename)

    current_time = datetime.now().isoformat()
    
    for asset in assets:
        symbol = asset["symbol"]
        price = asset["priceUsd"]
        volume = asset["volumeUsd24Hr"]
        source = "coincap_api"
        # Use current time as "ingestion" time, or API timestamp if available? 
        # API doesn't strictly give a "timestamp" for the snapshot, so we use now.
        
        # Ensure we don't have None values for the "clean" file
        if price is None: price = 0
        if volume is None: volume = 0
        
        data.append([symbol, price, volume, current_time, source])
        
    with open(filename, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    print(f"Generated {filename} with {len(data)} rows from real world data.")

def generate_legacy_csv(filename="legacy_crypto_data.csv"):
    """
    Generates a 'messy' legacy file from real data.
    Quirks: 'Ticker', 'LastPrice', 'Vol', 'RecordedDate' (DD-MM-YYYY)
    """
    headers = ["Ticker", "LastPrice", "Vol", "RecordedDate"]
    data = []
    
    assets = fetch_real_data()
    if not assets:
        return # Should have been caught above or we just count on the first call
    
    # Take a subset to simulate a different "legacy" source
    subset = assets[:50] 
    
    for i, asset in enumerate(subset):
        symbol = asset["symbol"]
        price = asset["priceUsd"]
        volume = asset["volumeUsd24Hr"]
        
        # Introduce Messiness
        
        # 1. Randomly malform some dates (or just use the legacy format)
        # Legacy format expectation from ingest_legacy.py: DD-MM-YYYY
        
        dt_obj = datetime.now()
        date_str = dt_obj.strftime("%d-%m-%Y %H:%M:%S")
        
        # 2. Occasional null volume
        if i % 10 == 0:
            volume = None
            
        # 3. Fuzzy Ticker rename for drift detection testing (e.g. "BTC" -> "BTC-USD" or "bitcoin")
        if i == 5:
            symbol = "BTC-Legacy" 

        data.append([symbol, price, volume, date_str])
        
    with open(filename, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    print(f"Generated {filename} with {len(data)} rows (Legacy Format).")

def generate_synthetic_csv(filename):
    # Fallback to original logic if API fails
    headers = ["symbol", "price", "volume", "timestamp", "source"]
    data = []
    start_date = datetime.now()
    symbols = ["BTC", "ETH", "SOL", "ADA", "DOGE"]
    for _ in range(100):
        symbol = random.choice(symbols)
        price = round(random.uniform(10, 50000), 2)
        volume = round(random.uniform(1000, 1000000), 2)
        timestamp = start_date.isoformat()
        source = "synthetic_fallback"
        data.append([symbol, price, volume, timestamp, source])
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    print(f"Generated {filename} (Synthetic Fallback).")

if __name__ == "__main__":
    generate_csv()
    generate_legacy_csv()
