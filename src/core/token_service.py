from fastapi import FastAPI, HTTPException
from core.rate_limiter import RateLimiter
import threading

app = FastAPI()

# 取引所ごとのレート制限設定
EXCHANGE_LIMITS = {
    "bybit": {
        "order_create": {"max_requests": 5, "interval": 60, "token_cost": 1},
        "market_ticker": {"max_requests": 25, "interval": 60, "token_cost": 0.04},
        "market_orderbook": {"max_requests": 50, "interval": 60, "token_cost": 0.02},
    },
    "binance": {
        "order_create": {"max_requests": 10, "interval": 60, "token_cost": 1},
        "market_ticker": {"max_requests": 20, "interval": 60, "token_cost": 0.05},
    },
    "okx": {
        "order_create": {"max_requests": 7, "interval": 60, "token_cost": 1},
        "market_ticker": {"max_requests": 15, "interval": 60, "token_cost": 0.06},
    },
}

limiter = RateLimiter(EXCHANGE_LIMITS)

@app.get("/token_status/{exchange}/{endpoint}")
def get_token_status(exchange: str, endpoint: str):
    """取引所＋エンドポイントごとの残りトークン数を取得"""
    if exchange in EXCHANGE_LIMITS and endpoint in EXCHANGE_LIMITS[exchange]:
        redis_key = f"{exchange}_{endpoint}_tokens"
        tokens = float(limiter.redis_client.get(redis_key) or 0)
        return {"exchange": exchange, "endpoint": endpoint, "remaining_tokens": tokens}
    raise HTTPException(status_code=404, detail="Exchange or endpoint not found")

@app.post("/consume_token/{exchange}/{endpoint}")
def consume_token(exchange: str, endpoint: str):
    """取引所＋エンドポイントごとのトークンを消費（許可 or 制限）"""
    if exchange in EXCHANGE_LIMITS and endpoint in EXCHANGE_LIMITS[exchange]:
        if limiter.consume_token(exchange, endpoint):
            return {"exchange": exchange, "endpoint": endpoint, "status": "allowed"}
        else:
            raise HTTPException(status_code=429, detail="Rate limit exceeded, try later")
    raise HTTPException(status_code=404, detail="Exchange or endpoint not found")

start_token_refill(limiter)  # サーバー起動時に自動補充を開始
