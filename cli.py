#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot — CLI entry point.

Usage:
  python cli.py --symbol BTCUSDT --side BUY  --type MARKET     --qty 0.001
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT       --qty 0.001 --price 100000
  python cli.py --symbol BTCUSDT --side BUY  --type STOP_LIMIT  --qty 0.001 --price 95500 --stop-price 96000
"""

import argparse
import os
import sys
import textwrap

from bot.client       import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging
from bot.orders       import dispatch_order, OrderResult
from bot.validators   import validate_all

SEP = "─" * 56


def print_request_summary(params: dict):
    print(f"\n{SEP}")
    print("  ORDER REQUEST SUMMARY")
    print(SEP)
    print(f"  Symbol     : {params['symbol']}")
    print(f"  Side       : {params['side']}")
    print(f"  Type       : {params['order_type']}")
    print(f"  Quantity   : {params['quantity']}")
    if params.get("price") is not None:
        print(f"  Limit Price: {params['price']}")
    if params.get("stop_price") is not None:
        print(f"  Stop Price : {params['stop_price']}")
    print(SEP)


def print_order_result(result: OrderResult):
    if result.success:
        print(f"\n{'✅  ORDER PLACED SUCCESSFULLY':^56}")
        print(SEP)
        print(f"  Order ID        : {result.order_id}")
        print(f"  Client Order ID : {result.client_order_id}")
        print(f"  Symbol          : {result.symbol}")
        print(f"  Side            : {result.side}")
        print(f"  Type            : {result.order_type}")
        print(f"  Status          : {result.status}")
        print(f"  Orig Qty        : {result.orig_qty}")
        print(f"  Executed Qty    : {result.executed_qty}")
        if result.avg_price:
            print(f"  Avg Fill Price  : {result.avg_price}")
        if result.price and result.price != "0":
            print(f"  Limit Price     : {result.price}")
        if result.stop_price and result.stop_price != "0":
            print(f"  Stop Price      : {result.stop_price}")
        if result.time_in_force:
            print(f"  Time In Force   : {result.time_in_force}")
        print(SEP + "\n")
    else:
        print(f"\n{'❌  ORDER FAILED':^56}")
        print(SEP)
        print(f"  Error : {result.error_message}")
        if result.error_code:
            print(f"  Code  : {result.error_code}")
        print(SEP + "\n")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
            Binance Futures Testnet Trading Bot
            ────────────────────────────────────
            Place MARKET, LIMIT, or STOP_LIMIT orders.
            Credentials from env vars: BINANCE_API_KEY / BINANCE_API_SECRET
        """),
        epilog=textwrap.dedent("""\
            Examples:
              python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
              python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 100000
              python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --qty 0.001 --price 95500 --stop-price 96000
        """),
    )
    parser.add_argument("--symbol", "-s", required=True, help="e.g. BTCUSDT")
    parser.add_argument("--side",         required=True, help="BUY or SELL")
    parser.add_argument("--type",  "-t",  required=True, dest="order_type",
                        help="MARKET | LIMIT | STOP_LIMIT")
    parser.add_argument("--qty",   "-q",  required=True, dest="quantity",
                        help="Quantity, e.g. 0.001")
    parser.add_argument("--price", "-p",  default=None,
                        help="Limit price (required for LIMIT / STOP_LIMIT)")
    parser.add_argument("--stop-price",   default=None, dest="stop_price",
                        help="Stop trigger price (required for STOP_LIMIT)")
    parser.add_argument("--log-dir",      default="logs",
                        help="Log folder (default: logs/)")
    return parser


def main():
    parser = build_parser()
    args   = parser.parse_args()

    logger = setup_logging(log_dir=args.log_dir)

    api_key    = os.getenv("BINANCE_API_KEY",    "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print("\n❌  Missing credentials.")
        print("    Set BINANCE_API_KEY and BINANCE_API_SECRET as environment variables.\n")
        logger.error("Credentials not set.")
        sys.exit(1)

    try:
        validated = validate_all(
            symbol     = args.symbol,
            side       = args.side,
            order_type = args.order_type,
            quantity   = args.quantity,
            price      = args.price,
            stop_price = args.stop_price,
        )
    except ValueError as exc:
        print(f"\n❌  Validation error: {exc}\n")
        logger.error("Validation error: %s", exc)
        sys.exit(1)

    print_request_summary(validated)

    try:
        client = BinanceClient(api_key=api_key, api_secret=api_secret)
    except ValueError as exc:
        print(f"\n❌  Client error: {exc}\n")
        sys.exit(1)

    result = dispatch_order(
        client     = client,
        symbol     = validated["symbol"],
        side       = validated["side"],
        order_type = validated["order_type"],
        quantity   = validated["quantity"],
        price      = validated["price"],
        stop_price = validated["stop_price"],
    )

    print_order_result(result)

    if not result.success:
        sys.exit(1)


if __name__ == "__main__":
    main()
