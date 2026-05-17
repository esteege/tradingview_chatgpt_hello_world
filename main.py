import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from openai import OpenAI
from pydantic import BaseModel, Field


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TV_WEBHOOK_SECRET = os.getenv("TV_WEBHOOK_SECRET", "change_me")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

client = OpenAI(api_key=OPENAI_API_KEY)

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "signals.jsonl"

app = FastAPI(title="TradingView to ChatGPT Hello World")


class TradingViewAlert(BaseModel):
    secret: str
    symbol: str = Field(default="UNKNOWN")
    timeframe: Optional[str] = None
    price: Optional[str] = None
    signal: str = Field(default="UNKNOWN")
    score: Optional[str] = None
    comment: Optional[str] = None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook/tradingview")
async def tradingview_webhook(request: Request) -> Dict[str, Any]:
    try:
        payload_raw = await request.json()
        alert = TradingViewAlert(**payload_raw)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}")

    if alert.secret != TV_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized webhook secret")

    prompt = build_prompt(alert)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a trading assistant."
            },
            {
                "role": "user",
                "content": f"""
    TradingView Alert

    signal_text = f"""
    TradingView Alert
    Symbol: {data.get("symbol")}
    Signal: {data.get("signal")}
    Price: {data.get("price")}
    Timeframe: {data.get("timeframe")}
    Score: {data.get("score")}
    Comment: {data.get("comment")}
    """
            }
        ]
    )
    
    ai_text = response.choices[0].message.content

    log_record = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "alert": alert.model_dump(),
        "ai_response": ai_text,
    }

    append_jsonl(LOG_FILE, log_record)

    return {
        "status": "received",
        "symbol": alert.symbol,
        "signal": alert.signal,
        "ai_response": ai_text,
    }


def build_prompt(alert: TradingViewAlert) -> str:
    return f"""
You are Eric's trading signal assistant.

This is a HELLO WORLD webhook test from TradingView.

Analyze the alert, but do not recommend real-money execution.
Return a compact JSON-style response with:
- summary
- signal_quality
- risk_notes
- suggested_action

TradingView alert:
symbol: {alert.symbol}
timeframe: {alert.timeframe}
price: {alert.price}
signal: {alert.signal}
score: {alert.score}
comment: {alert.comment}

Allowed suggested_action values:
WATCH, PAPER, REJECT

Remember: this is only a webhook plumbing test.
""".strip()


def append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
