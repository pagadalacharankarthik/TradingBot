# Binance Futures Testnet Trading Bot

A Python CLI trading bot for Binance Futures Testnet (USDT-M).
Supports MARKET, LIMIT, and STOP_LIMIT orders with full logging and validation.

---

## Project Structure

```
trading_bot_v2/
├── bot/
│   ├── __init__.py          <- package marker (required)
│   ├── client.py            <- Binance REST client (auth + HTTP + clock sync)
│   ├── orders.py            <- order placement logic
│   ├── validators.py        <- input validation
│   └── logging_config.py   <- logging setup
├── cli.py                   <- CLI entry point
├── logs/                    <- auto-created log files go here
├── README.md
└── requirements.txt
```

---

## Step 1 — Install Python

1. Go to https://python.org/downloads
2. Download Python 3.11 or newer
3. Run the installer
4. IMPORTANT: On the first screen tick the box that says "Add Python to PATH"
5. Click Install Now

Verify it worked — open CMD and type:
```
python --version
```
You should see: Python 3.11.x

---

## Step 2 — Get Testnet API Keys

1. Open browser and go to:  https://testnet.binancefuture.com
2. Click "Login with GitHub"  (no phone, no ID, no verification needed)
3. After login click the "API Key" tab at the top of the page
4. Click the "Generate" button
5. COPY BOTH keys immediately and paste them into Notepad
   - API Key    (long string starting with letters)
   - Secret Key (another long string — shown only once, never again)

---

## Step 3 — Open CMD Inside the Project Folder

1. Extract the zip file to your Desktop or any folder
2. Open File Explorer and go into the trading_bot_v2 folder
   (the one that contains cli.py and requirements.txt)
3. Click the address bar at the top of File Explorer
   (it shows the folder path like C:\Users\...)
4. Type:  cmd
5. Press Enter
6. A black CMD window opens directly inside the correct folder

You should see something like:
```
C:\Users\YourName\Desktop\trading_bot_v2>
```

---

## Step 4 — Install Requirements

Type this command and press Enter:
```
python -m pip install -r requirements.txt
```

You will see it downloading and installing. Wait for it to finish.
You only need to do this once.

---

## Step 5 — Set Your API Keys

Copy these two lines, replace the values with YOUR keys, paste into CMD and press Enter:
```
set BINANCE_API_KEY=paste_your_api_key_here
set BINANCE_API_SECRET=paste_your_secret_key_here
```

Example (do not use these, they are fake):
```
set BINANCE_API_KEY=XJNih3lXT00AjOwYzW2PZwV56aM
set BINANCE_API_SECRET=OnrFkf8MtSLEMcnsawIJmZfn7bO
```

IMPORTANT RULES:
- No spaces around the = sign
- No quotes around the key
- Must do this every time you open a new CMD window
- To check they are set correctly type:  echo %BINANCE_API_KEY%

---

## Step 6 — Run All 3 Order Types

Copy and paste each command one by one and press Enter.
Wait for the result before running the next one.


### MARKET Order (executes immediately)
```
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
```
Expected result:  Status = FILLED


### LIMIT Order (waits for price)
```
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 100000
```
Expected result:  Status = NEW  (this is correct — it is waiting for price to hit 100000)


### STOP_LIMIT Order (bonus)
```
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --qty 0.001 --price 95500 --stop-price 96000
```
Expected result:  Status = NEW  (waiting for stop price to trigger)


---

## All Commands at Once — Full Session

Open CMD in the project folder, then run these lines one by one:

```
python -m pip install -r requirements.txt
set BINANCE_API_KEY=paste_your_api_key_here
set BINANCE_API_SECRET=paste_your_secret_key_here
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 100000
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --qty 0.001 --price 95500 --stop-price 96000
```

---

## All Available Commands

### Market Orders
```
python cli.py --symbol BTCUSDT --side BUY  --type MARKET --qty 0.001
python cli.py --symbol BTCUSDT --side SELL --type MARKET --qty 0.001
python cli.py --symbol ETHUSDT --side BUY  --type MARKET --qty 0.01
python cli.py --symbol ETHUSDT --side SELL --type MARKET --qty 0.01
```

### Limit Orders
```
python cli.py --symbol BTCUSDT --side BUY  --type LIMIT --qty 0.001 --price 80000
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 100000
python cli.py --symbol ETHUSDT --side BUY  --type LIMIT --qty 0.01  --price 2000
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --qty 0.01  --price 5000
```

### Stop-Limit Orders (bonus)
```
python cli.py --symbol BTCUSDT --side BUY  --type STOP_LIMIT --qty 0.001 --price 95500 --stop-price 96000
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --qty 0.001 --price 93500 --stop-price 94000
```

### Help
```
python cli.py --help
```

---

## What the Output Means

```
Status: FILLED    ->  Market order executed immediately       (success)
Status: NEW       ->  Limit order waiting for price to hit   (success)
Status: NEW       ->  Stop-limit waiting for trigger price   (success)
```

Error codes:
```
-1021  ->  Clock out of sync. Run:  w32tm /resync /force  in admin CMD
-2014  ->  API key is wrong. Re-copy it from testnet site
-1121  ->  Wrong symbol. Use BTCUSDT or ETHUSDT exactly
-1111  ->  Quantity too many decimals. Use 0.001 not 0.0001
```

---

## Where Are My Log Files?

After running any order, a log file is automatically created at:
```
logs/trading_bot_YYYYMMDD.log
```

To view it in CMD:
```
type logs\trading_bot_20250115.log
```
Replace 20250115 with today's date.

---

## Assumptions

- USDT-M Futures testnet only (https://testnet.binancefuture.com)
- One-way position mode (hedge mode OFF — the testnet default)
- timeInForce = GTC (Good Till Cancelled) for all LIMIT orders
- API credentials via environment variables — no config file needed
- STOP_LIMIT maps to Binance internal "STOP" order type on futures
- Bot auto-syncs with Binance server time on startup to avoid -1021 errors

---
<!-- ### 🛠️ Built with ❤️ by Pagadala Charan Karthik -->
<p align="center">
  Built with ❤️ by <b>Pagadala Charan Karthik</b>
</p>

## 👨‍💻 Connect With Me



* **LinkedIn:** [Connect with me](https://www.linkedin.com/in/pagadala-charan-karthik-67a614354/)
* **Email:** [charankarthik366@gmail.com](mailto:charankarthik366@gmail.com)
* **Portfolio:** [Connect with me](https://pagadala-charan-karthik.netlify.app/)

