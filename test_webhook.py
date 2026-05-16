import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "http://127.0.0.1:8000/webhook/tradingview"

payload = {
    "secret": os.getenv("TV_WEBHOOK_SECRET", "change_me"),
    "symbol": "MES1!",
    "timeframe": "5",
    "price": "5325.25",
    "signal": "validScoutLong",
    "score": "5/5",
    "comment": "Hello World Scout Signal"
}

response = requests.post(url, json=payload, timeout=30)

print("Status:", response.status_code)
print(response.json())
