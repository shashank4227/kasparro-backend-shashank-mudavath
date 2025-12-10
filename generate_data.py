import csv
import random
from datetime import datetime, timedelta

def generate_csv(filename="crypto_data.csv", rows=100):
    headers = ["symbol", "price", "volume", "timestamp", "source"]
    data = []
    
    start_date = datetime.now() - timedelta(days=7)
    
    symbols = ["BTC", "ETH", "SOL", "ADA", "DOGE"]
    
    for _ in range(rows):
        symbol = random.choice(symbols)
        price = round(random.uniform(10, 50000), 2)
        volume = round(random.uniform(1000, 1000000), 2)
        timestamp = (start_date + timedelta(minutes=random.randint(0, 10000))).isoformat()
        source = "synthetic_exchange"
        
        data.append([symbol, price, volume, timestamp, source])
        
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    print(f"Generated {filename} with {rows} rows.")

def generate_legacy_csv(filename="legacy_crypto_data.csv", rows=50):
    # Quirks: 'Ticker', 'LastPrice', 'Vol', 'RecordedDate' (DD-MM-YYYY)
    headers = ["Ticker", "LastPrice", "Vol", "RecordedDate"]
    data = []
    
    start_date = datetime.now() - timedelta(days=7)
    symbols = ["DOT", "AVAX", "LTC", "LINK", "XLM"]
    
    for _ in range(rows):
        symbol = random.choice(symbols)
        price = round(random.uniform(5, 500), 2)
        volume = round(random.uniform(5000, 500000), 2)
        # Quirk: DD-MM-YYYY format
        timestamp = (start_date + timedelta(minutes=random.randint(0, 10000)))
        date_str = timestamp.strftime("%d-%m-%Y %H:%M:%S")
        
        data.append([symbol, price, volume, date_str])
        
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    print(f"Generated {filename} with {rows} rows.")

if __name__ == "__main__":
    generate_csv()
    generate_legacy_csv()
