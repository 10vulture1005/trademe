import time
import hmac
import hashlib
import json
import requests
from urllib.parse import urlparse, urlencode
from app.core.config import settings



class DeltaService:
    def __init__(self):
        self.api_key = settings.DELTA_API_KEY
        self.api_secret = settings.DELTA_API_SECRET
        self.base_url = settings.DELTA_BASE_URL
        self.enabled = bool(self.api_key and self.api_secret)

    def _generate_signature(self, method: str, path: str, query_params: str, payload_str: str, timestamp: str) -> str:
        """
        Generates HMAC-SHA256 signature for Delta Exchange.
        Signature = hmac(secret, method + timestamp + path + query + body, sha256)
        """
        msg = f"{method}{timestamp}{path}{query_params}{payload_str}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            msg.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def request(self, method: str, endpoint: str, params: dict = None, payload: dict = None):
        if not self.enabled:
            raise Exception("Delta Exchange API Keys not configured.")

        timestamp = str(int(time.time()))
        
        path = f"/v2{endpoint}" # Assuming V2, but check docs if strict
        # Note: Delta path in signature usually includes /v2
        
        # Prepare body and query
        # Use compact JSON separators to ensure consistency and minimize size
        payload_str = json.dumps(payload, separators=(',', ':')) if payload else ""
        query_str = urlencode(params) if params else ""
        
        full_url = f"{self.base_url}{path}"
        if query_str:
            full_url += f"?{query_str}"

        signature = self._generate_signature(
            method.upper(), 
            path, 
            query_str, 
            payload_str, 
            timestamp
        )

        headers = {
            "Accept": "application/json",
            "api-key": self.api_key,
            "timestamp": timestamp,
            "signature": signature,
            "User-Agent": "TradingRiskGovernor/1.0"
        }
        if payload:
            headers["Content-Type"] = "application/json"

        try:
            response = requests.request(
                method, 
                full_url, 
                headers=headers, 
                data=payload_str if payload else None,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Parse Delta specific error if possible
            error_msg = f"HTTP Error: {str(e)}"
            try:
                # Try to get more details from response text
                print(f"Debug - Response Text: {e.response.text}")
                err_data = e.response.json()
                error_msg = f"Delta API Error: {err_data}"
            except:
                pass
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Connection Failed: {str(e)}")

    def place_order(self, symbol: str, side: str, size: float, limit_price: float = None):
        """
        Places an order on Delta Exchange.
        Side: buy | sell (converted from LONG/SHORT)
        """
        # Map internal 'LONG'/'SHORT' to Delta 'buy'/'sell' or ensure correctness
        # Delta usually uses 'buy' / 'sell' for spot/futures
        delta_side = "buy" if side.lower() == "long" else "sell" if side.lower() == "short" else side.lower()
        
        # Determine order type
        order_type = "limit_order" if limit_price and limit_price > 0 else "market_order"
        
        payload = {
            "product_symbol": symbol,
            "size": size,
            "side": delta_side,
            "order_type": order_type
        }
        
        if order_type == "limit_order":
            payload["limit_price"] = str(limit_price)

        return self.request("POST", "/orders", payload=payload)

    def get_wallet_balance(self):
        return self.request("GET", "/wallet/balances")

    def get_mark_price(self, symbol: str) -> float:
        # Delta Ticker Endpoint: /v2/tickers/{symbol}
        # Returns { "result": { "mark_price": ... }, "success": true }
        try:
            data = self.request("GET", f"/tickers/{symbol}")
            result = data.get("result", {})
            return float(result.get("mark_price", 0))
        except Exception as e:
             print(f"Error fetching mark price for {symbol}: {e}")
             return 0.0

delta_service = DeltaService()
