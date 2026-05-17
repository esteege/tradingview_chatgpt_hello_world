from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class TradingViewAlert(BaseModel):
    secret: str
    symbol: str
    timeframe: str
    price: str
    signal: str
    score: str
    comment: str


@app.get("/")
def health_check():
    return {"status": "ok"}


def build_prompt(alert: TradingViewAlert) -> str:
    return f"""
You are Eric's trading signal assistant.

Analyze the TradingView alert and return a concise trading interpretation.

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
- observe
- paper_trade
- ignore

Keep the response short and practical.
"""


@app.post("/webhook/tradingview")
async def tradingview_webhook(alert: TradingViewAlert):

    prompt = build_prompt(alert)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a concise trading assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=300
    )

    ai_text = response.choices[0].message.content

    return {
        "status": "success",
        "symbol": alert.symbol,
        "signal": alert.signal,
        "ai_response": ai_text
    }
