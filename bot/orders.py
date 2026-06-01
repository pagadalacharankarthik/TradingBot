"""
Order placement logic — MARKET, LIMIT, STOP_LIMIT.
Returns a clean OrderResult dataclass for consistent handling.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .client import BinanceClient, BinanceAPIError

logger = logging.getLogger("trading_bot.orders")

ORDER_ENDPOINT = "/fapi/v1/order"


@dataclass
class OrderResult:
    success:         bool
    order_id:        int    = None
    client_order_id: str    = None
    symbol:          str    = None
    side:            str    = None
    order_type:      str    = None
    status:          str    = None
    orig_qty:        str    = None
    executed_qty:    str    = None
    avg_price:       str    = None
    price:           str    = None
    stop_price:      str    = None
    time_in_force:   str    = None
    raw:             dict   = field(default_factory=dict)
    error_message:   str    = None
    error_code:      int    = None

    @classmethod
    def from_response(cls, data: dict) -> "OrderResult":
        return cls(
            success         = True,
            order_id        = data.get("orderId"),
            client_order_id = data.get("clientOrderId"),
            symbol          = data.get("symbol"),
            side            = data.get("side"),
            order_type      = data.get("type"),
            status          = data.get("status"),
            orig_qty        = data.get("origQty"),
            executed_qty    = data.get("executedQty"),
            avg_price       = data.get("avgPrice"),
            price           = data.get("price"),
            stop_price      = data.get("stopPrice"),
            time_in_force   = data.get("timeInForce"),
            raw             = data,
        )

    @classmethod
    def from_error(cls, message: str, code: int = None) -> "OrderResult":
        return cls(success=False, error_message=message, error_code=code)


def _place_order(client: BinanceClient, params: dict) -> OrderResult:
    logger.info("Placing %s %s | symbol=%s qty=%s price=%s",
                params.get("side"), params.get("type"),
                params.get("symbol"), params.get("quantity"),
                params.get("price", "MARKET"))
    try:
        data   = client.post(ORDER_ENDPOINT, params=params)
        result = OrderResult.from_response(data)
        logger.info("Order placed ✓ | orderId=%s status=%s executedQty=%s avgPrice=%s",
                    result.order_id, result.status,
                    result.executed_qty, result.avg_price)
        return result
    except BinanceAPIError as exc:
        logger.error("Order failed | code=%s msg=%s", exc.code, str(exc))
        return OrderResult.from_error(str(exc), exc.code)
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        return OrderResult.from_error(f"Unexpected error: {exc}")


def place_market_order(client, symbol, side, quantity) -> OrderResult:
    return _place_order(client, {
        "symbol":   symbol,
        "side":     side,
        "type":     "MARKET",
        "quantity": quantity,
    })


def place_limit_order(client, symbol, side, quantity, price, time_in_force="GTC") -> OrderResult:
    return _place_order(client, {
        "symbol":      symbol,
        "side":        side,
        "type":        "LIMIT",
        "quantity":    quantity,
        "price":       price,
        "timeInForce": time_in_force,
    })


def place_stop_limit_order(client, symbol, side, quantity, price, stop_price, time_in_force="GTC") -> OrderResult:
    return _place_order(client, {
        "symbol":      symbol,
        "side":        side,
        "type":        "STOP",
        "quantity":    quantity,
        "price":       price,
        "stopPrice":   stop_price,
        "timeInForce": time_in_force,
    })


def dispatch_order(client, symbol, side, order_type, quantity, price=None, stop_price=None) -> OrderResult:
    if order_type == "MARKET":
        return place_market_order(client, symbol, side, quantity)
    elif order_type == "LIMIT":
        return place_limit_order(client, symbol, side, quantity, price)
    elif order_type == "STOP_LIMIT":
        return place_stop_limit_order(client, symbol, side, quantity, price, stop_price)
    else:
        return OrderResult.from_error(f"Unsupported order type: {order_type}")
