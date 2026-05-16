# TradingView → ChatGPT Hello World

A minimal webhook pattern:

TradingView Alert → FastAPI webhook → OpenAI prompt → JSON response + local log.

## 1. Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key
TV_WEBHOOK_SECRET=change_me
OPENAI_MODEL=gpt-4.1-mini
```

## 2. Run locally

```bash
uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## 3. Simulate a TradingView webhook

```bash
python test_webhook.py
```

Or:

```bash
curl -X POST http://127.0.0.1:8000/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "change_me",
    "symbol": "MES1!",
    "timeframe": "5",
    "price": "5325.25",
    "signal": "validScoutLong",
    "score": "5/5",
    "comment": "Hello World Scout Signal"
  }'
```

## 4. TradingView alert body

Use JSON like this in your TradingView alert message:

```json
{
  "secret": "change_me",
  "symbol": "{{ticker}}",
  "timeframe": "{{interval}}",
  "price": "{{close}}",
  "signal": "validScoutLong",
  "score": "5/5",
  "comment": "{{strategy.order.comment}}"
}
```

## 5. Deploy pattern

For public webhook testing, use one of these:

- `ngrok http 8000`
- Render
- Railway
- Fly.io
- Cloudflare Workers + separate Python service

TradingView webhook URL should point to:

```text
https://your-domain.com/webhook/tradingview
```
