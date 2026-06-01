"""
Input validation for CLI arguments.
All validation errors raise ValueError with a clear human-readable message.
"""

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.isalpha() or len(symbol) < 3:
        raise ValueError(
            f"Invalid symbol '{symbol}'. Expected alphabetic string like BTCUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than zero, got {qty}.")
    return qty


def validate_price(price, order_type: str):
    if order_type == "MARKET":
        if price is not None:
            raise ValueError("Price should not be provided for MARKET orders.")
        return None

    if price is None:
        raise ValueError(f"Price is required for {order_type} orders.")

    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValueError(f"Price must be greater than zero, got {p}.")
    return p


def validate_stop_price(stop_price, order_type: str):
    if order_type != "STOP_LIMIT":
        return None

    if stop_price is None:
        raise ValueError("--stop-price is required for STOP_LIMIT orders.")

    try:
        sp = float(stop_price)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
    if sp <= 0:
        raise ValueError(f"Stop price must be greater than zero, got {sp}.")
    return sp


def validate_all(symbol, side, order_type, quantity, price=None, stop_price=None) -> dict:
    order_type = validate_order_type(order_type)
    return {
        "symbol":     validate_symbol(symbol),
        "side":       validate_side(side),
        "order_type": order_type,
        "quantity":   validate_quantity(quantity),
        "price":      validate_price(price, order_type),
        "stop_price": validate_stop_price(stop_price, order_type),
    }
