# Stock Analyzer Pro — BSc IT Final-Year Project

A Streamlit + Python + SQLite stock research dashboard inspired by the uploaded Stock Analyzer Black Book. It includes:
- User registration/login with salted PBKDF2-HMAC-SHA256 password hashes
- Live/latest available quotes and historical price charts using Yahoo Finance via `yfinance`
- Company fundamentals when the provider supplies them
- Watchlist stored per user
- Portfolio transaction ledger (BUY/SELL) with estimated holdings and unrealized P/L
- Stock comparison normalized to a common base of 100
- Technical indicators: SMA 20/50, EMA 12/26, MACD, RSI(14), Bollinger Bands
- Historical-data Random Forest next-session estimate with time-ordered holdout MAE
- Risk analysis: annualized volatility/return, maximum drawdown and Sharpe ratio
- Headline sentiment estimate using a transparent word lexicon

## Requirements
- Python 3.10 or newer recommended
- Internet connection for market data and news
- Windows, macOS or Linux
- No paid API key is required for the default Yahoo Finance data source, but data availability, latency and limits are controlled by the provider.

## Run on Windows
1. Extract the ZIP to a folder, for example `StockAnalyzerPro`.
2. Open Command Prompt/PowerShell in that folder.
3. Create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

4. Install packages:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Launch the app:

```powershell
streamlit run app.py
```

6. Your browser should open. Create an account on the **Create account** tab, then log in.

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Example ticker symbols
- India: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `^NSEI`
- US: `AAPL`, `MSFT`, `NVDA`, `GOOGL`
Use the provider's ticker format. Some indexes may not provide all fundamentals.

## Main files
- `app.py` — Streamlit user interface and pages
- `db.py` — SQLite schema, account security and user-specific records
- `market_data.py` — market/history/news retrieval and caching
- `analytics.py` — indicators, risk metrics, comparison and prediction
- `sentiment.py` — lightweight explainable headline sentiment scoring
- `tests/test_analytics.py` — basic automated tests

## Important design notes
- The Yahoo Finance interface is unofficial and can change. It may be delayed, incomplete or unavailable for some tickers.
- The app is an educational prototype, not a brokerage platform or production financial service.
- The prediction model uses historical price-derived features. It does not know future events, corporate announcements or macroeconomic changes; output is not investment advice.
- The sentiment module is a simple lexicon baseline, not a finance-trained language model. Negation, sarcasm and context can be missed.
- Portfolio calculations are a student-project estimate. Taxes, brokerage, dividends, splits, FX and advanced accounting are not modelled.
- This prototype includes user login, but is not hardened for public deployment. Do not expose it publicly without professional security review, rate limiting, secure hosting and additional controls.

## Troubleshooting
- **No data / ticker error:** Check spelling and provider ticker suffix; try `TCS.NS` or `AAPL`.
- **Yahoo throttling:** Wait and retry; cached requests reduce repeated calls.
- **Package installation error:** Use Python 3.10+ and install inside the activated virtual environment.
- **Port already in use:** Run `streamlit run app.py --server.port 8502`.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Suggested project flow (for viva)
Browser/UI → Streamlit pages → market data module → analytics/prediction modules → SQLite for users/watchlist/trades → interactive Plotly charts.

## Reference alignment
The supplied Black Book outlines a centralized dashboard, stock search, historical charts, fundamentals, login, watchlist, portfolio, modular architecture and class/ER/activity/DFD diagrams. This implementation uses Streamlit consistently rather than mixing Flask and Streamlit, and SQLite for persistent user-specific records.
