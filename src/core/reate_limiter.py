import redis
import time
import threading

class RateLimiter:
    """複数の取引所を一括管理するトークンプール"""

    def __init__(self, exchange_limits):
        """
        :param exchange_limits: 
            {
                "bybit": {"order_create": {"max_requests": 5, "interval": 60, "token_cost": 1}, ...},
                "binance": {"order_create": {"max_requests": 10, "interval": 60, "token_cost": 1}, ...}
            }
        """
        self.exchange_limits = exchange_limits
        self.redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self._init_token_pools()

    def _init_token_pools(self):
        """各取引所・エンドポイントごとのトークンプールを初期化"""
        for exchange, endpoints in self.exchange_limits.items():
            for endpoint, config in endpoints.items():
                redis_key = f"{exchange}_{endpoint}_tokens"
                if not self.redis_client.exists(redis_key):
                    self.redis_client.set(redis_key, config["max_requests"])

    def consume_token(self, exchange, endpoint):
        """エンドポイントごとのトークンを消費"""
        redis_key = f"{exchange}_{endpoint}_tokens"
        tokens = float(self.redis_client.get(redis_key) or 0)
        token_cost = self.exchange_limits[exchange][endpoint]["token_cost"]

        if tokens >= token_cost:
            self.redis_client.decrbyfloat(redis_key, token_cost)
            return True
        return False

    def refill_tokens(self):
        """一定時間ごとに取引所ごと・エンドポイントごとのトークンを補充"""
        while True:
            for exchange, endpoints in self.exchange_limits.items():
                for endpoint, config in endpoints.items():
                    redis_key = f"{exchange}_{endpoint}_tokens"
                    self.redis_client.set(redis_key, config["max_requests"])
            time.sleep(60)  # 1分ごとにリセット

def start_token_refill(limiter):
    """バックグラウンドでトークン補充を開始"""
    threading.Thread(target=limiter.refill_tokens, daemon=True).start()
