"""
Binance Futures Testnet REST client.
Handles HMAC-SHA256 signing, HTTP requests, logging, and error handling.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"
RECV_WINDOW = 60000


class BinanceAPIError(Exception):
    def __init__(self, message: str, code=None, http_status=None):
        super().__init__(message)
        self.code = code
        self.http_status = http_status


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL, timeout: int = 10):
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must not be empty.")

        self._api_key    = api_key
        self._api_secret = api_secret.encode()
        self.base_url    = base_url.rstrip("/")
        self.timeout     = timeout

        self._session = requests.Session()
        self._session.headers.update({
            "X-MBX-APIKEY": self._api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

        logger.info("BinanceClient ready. URL: %s", self.base_url)

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _sign(self, params: dict) -> dict:
        params["timestamp"]  = self._timestamp()
        params["recvWindow"] = RECV_WINDOW
        query     = urlencode(params)
        signature = hmac.new(self._api_secret, query.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def _handle_response(self, response: requests.Response) -> dict:
        logger.debug("HTTP %s %s → %s | %s",
                     response.request.method, response.url,
                     response.status_code, response.text[:500])

        try:
            data = response.json()
        except ValueError:
            raise BinanceAPIError(
                f"Non-JSON response (HTTP {response.status_code}): {response.text[:200]}",
                http_status=response.status_code,
            )

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceAPIError(
                message=data.get("msg", "Unknown Binance error"),
                code=data["code"],
                http_status=response.status_code,
            )

        if not response.ok:
            raise BinanceAPIError(
                f"HTTP {response.status_code}: {response.text[:200]}",
                http_status=response.status_code,
            )

        return data

    def get(self, endpoint: str, params: dict = None, signed: bool = False):
        params = params or {}
        if signed:
            params = self._sign(params)
        url = f"{self.base_url}{endpoint}"
        logger.debug("GET %s", url)
        try:
            response = self._session.get(url, params=params, timeout=self.timeout)
        except requests.exceptions.ConnectionError as exc:
            raise BinanceAPIError(f"Network error: {exc}") from exc
        except requests.exceptions.Timeout:
            raise BinanceAPIError("Request timed out.")
        return self._handle_response(response)

    def post(self, endpoint: str, params: dict = None):
        params = params or {}
        params = self._sign(params)
        url = f"{self.base_url}{endpoint}"
        logger.debug("POST %s | params=%s", url,
                     {k: v for k, v in params.items() if k != "signature"})
        try:
            response = self._session.post(url, data=params, timeout=self.timeout)
        except requests.exceptions.ConnectionError as exc:
            raise BinanceAPIError(f"Network error: {exc}") from exc
        except requests.exceptions.Timeout:
            raise BinanceAPIError("Request timed out.")
        return self._handle_response(response)
