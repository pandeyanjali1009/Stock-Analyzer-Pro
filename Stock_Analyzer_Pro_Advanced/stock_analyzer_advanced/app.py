import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from db import init_db, create_user, authenticate_user, add_watchlist, get_watchlist, remove_watchlist, add_trade, get_trades, delete_trade
from market_data import get_history, get_quote, get_news
from analytics import add_indicators, calculate_risk, predict_next_close, compare_performance
from sentiment import score_news

st.set_page_config(page_title="Stock Analyzer Pro", page_icon="📈", layout="wide")
init_db()

st.markdown("""
<style>
.block-container {padding-top: 1.3rem;}
[data-testid="stMetric"] {background: rgba(100,130,180,.08); padding: 12px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

def fmt_money(x, currency="₹"):
    try:
        return f"{currency}{float(x):,.2f}"
    except (TypeError, ValueError):
        return "N/A"

def auth_screen():
    st.title("📈 Stock Analyzer Pro")
    st.caption("BSc IT Final-Year Project • Market research, analytics and portfolio tracking")
    tab1, tab2 = st.tabs(["Login", "Create account"])
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            user = authenticate_user(username.strip(), password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Login failed. Check your username and password.")
    with tab2:
        with st.form("register_form"):
            username = st.text_input("Choose username", key="reg_user")
            email = st.text_input("Email (optional)", key="reg_email")
            password = st.text_input("Password (minimum 8 characters)", type="password", key="reg_pass")
            confirm = st.text_input("Confirm password", type="password", key="reg_confirm")
            submitted = st.form_submit_button("Create account", use_container_width=True)
        if submitted:
            if len(username.strip()) < 3:
                st.error("Username must contain at least 3 characters.")
            elif len(password) < 8:
                st.error("Use a password with at least 8 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                ok, msg = create_user(username.strip(), email.strip(), password)
                (st.success if ok else st.error)(msg)

if "user" not in st.session_state:
    auth_screen()
    st.stop()

user = st.session_state.user
user_id, username, role = user

with st.sidebar:
    st.title("📈 Stock Analyzer")
    st.write(f"Signed in as **{username}**")
    page = st.radio("Navigation", ["Market Dashboard", "Technical Analysis", "Compare Stocks", "AI Prediction", "Risk Analysis", "Portfolio", "Watchlist", "News Sentiment"])
    st.divider()
    if st.button("Log out", use_container_width=True):
        del st.session_state.user
        st.rerun()
    st.caption("Market data may be delayed and is provided for educational use.")

def get_ticker_input(key="ticker", default="RELIANCE.NS"):
    return st.text_input("Ticker symbol (e.g. RELIANCE.NS, TCS.NS, AAPL)", value=default, key=key).strip().upper()

def render_price_chart(df, ticker, candles=True):
    fig = go.Figure()
    if candles:
        fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name=ticker))
    else:
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
    fig.update_layout(title=f"{ticker} • Historical Price", xaxis_title="Date", yaxis_title="Price", height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

if page == "Market Dashboard":
    st.title("Market Dashboard")
    ticker = get_ticker_input()
    period = st.selectbox("History period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    if st.button("Load market data", type="primary"):
        st.session_state.dashboard_ticker = ticker
        st.session_state.dashboard_period = period
    ticker = st.session_state.get("dashboard_ticker", ticker)
    period = st.session_state.get("dashboard_period", period)
    try:
        quote = get_quote(ticker)
        hist = get_history(ticker, period)
        if hist.empty:
            st.warning("No price history found. Check the ticker and try again.")
        else:
            last = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else last
            change = last - prev
            change_pct = (change / prev * 100) if prev else 0
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Latest close", fmt_money(last), f"{change_pct:+.2f}%")
            c2.metric("Previous close", fmt_money(prev))
            c3.metric("Volume", f"{int(hist['Volume'].iloc[-1]):,}" if "Volume" in hist else "N/A")
            c4.metric("Currency", quote.get("currency") or "Market currency")
            render_price_chart(hist, ticker)
            with st.expander("Company fundamentals"):
                left, right = st.columns(2)
                for col, keys in [(left, ["longName", "sector", "industry", "marketCap"]), (right, ["trailingPE", "forwardPE", "trailingEps", "dividendYield"])]:
                    for k in keys:
                        val = quote.get(k)
                        if val is not None:
                            col.write(f"**{k}:** {val:,.4g}" if isinstance(val, (int, float)) else f"**{k}:** {val}")
            if st.button("Add to watchlist"):
                ok, msg = add_watchlist(user_id, ticker)
                (st.success if ok else st.info)(msg)
    except Exception as e:
        st.error(f"Could not load market data: {e}")
        st.info("Check internet access and the ticker symbol. Data availability depends on the provider.")

elif page == "Technical Analysis":
    st.title("Technical Analysis")
    ticker = get_ticker_input("technical_ticker")
    period = st.selectbox("Period", ["3mo", "6mo", "1y", "2y"], index=2, key="tech_period")
    if st.button("Calculate indicators", type="primary"):
        try:
            df = add_indicators(get_history(ticker, period))
            if df.empty:
                st.warning("No data available.")
            else:
                last = df.iloc[-1]
                cols = st.columns(4)
                for col, label, value in [
                    (cols[0], "RSI (14)", last.get("RSI")),
                    (cols[1], "MACD", last.get("MACD")),
                    (cols[2], "20-day SMA", last.get("SMA20")),
                    (cols[3], "50-day SMA", last.get("SMA50"))]:
                    col.metric(label, f"{value:.2f}" if pd.notna(value) else "N/A")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
                for col in ["SMA20", "SMA50", "BB_upper", "BB_lower"]:
                    if col in df:
                        fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, line=dict(width=1)))
                fig.update_layout(title=f"{ticker}: Price, Moving Averages & Bollinger Bands", height=480)
                st.plotly_chart(fig, use_container_width=True)
                macdfig = go.Figure()
                macdfig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"))
                macdfig.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], name="Signal"))
                macdfig.update_layout(title="MACD", height=300)
                st.plotly_chart(macdfig, use_container_width=True)
                st.dataframe(df.tail(15).round(3), use_container_width=True)
        except Exception as e:
            st.error(f"Indicator calculation failed: {e}")

elif page == "Compare Stocks":
    st.title("Compare Stocks")
    tickers_text = st.text_input("Enter up to 5 tickers separated by commas", "RELIANCE.NS,TCS.NS,INFY.NS")
    period = st.selectbox("Comparison period", ["1mo", "3mo", "6mo", "1y", "2y"], index=3, key="cmp_period")
    if st.button("Compare", type="primary"):
        tickers = list(dict.fromkeys([x.strip().upper() for x in tickers_text.split(",") if x.strip()]))[:5]
        try:
            result = compare_performance(tickers, period)
            if result.empty:
                st.warning("No comparable data returned.")
            else:
                st.plotly_chart(result, use_container_width=True)
                st.caption("Each series is indexed to 100 at the beginning of the selected period.")
        except Exception as e:
            st.error(f"Comparison failed: {e}")

elif page == "AI Prediction":
    st.title("AI Price Prediction (Educational)")
    st.warning("This is a simple historical-data model, not a reliable forecast or investment recommendation.")
    ticker = get_ticker_input("prediction_ticker")
    period = st.selectbox("Training history", ["1y", "2y", "5y", "10y"], index=1, key="pred_period")
    if st.button("Train model and estimate next close", type="primary"):
        try:
            hist = get_history(ticker, period)
            result = predict_next_close(hist)
            if result.get("error"):
                st.warning(result["error"])
            else:
                a, b, c = st.columns(3)
                a.metric("Latest close", fmt_money(result["last_close"]))
                b.metric("Model estimate (next session)", fmt_money(result["prediction"]))
                delta = (result["prediction"] / result["last_close"] - 1) * 100 if result["last_close"] else 0
                c.metric("Estimated change", f"{delta:+.2f}%")
                st.write(f"Model: **{result['model']}** • Test MAE: **{result['mae']:.3f}**")
                st.line_chart(pd.DataFrame({"Actual": result["actual"], "Predicted": result["predicted"]}))
                st.caption("Past performance does not guarantee future results. Model error can be large, especially around market events.")
        except Exception as e:
            st.error(f"Prediction failed: {e}")

elif page == "Risk Analysis":
    st.title("Risk Analysis")
    ticker = get_ticker_input("risk_ticker")
    period = st.selectbox("Risk window", ["3mo", "6mo", "1y", "2y", "5y"], index=2, key="risk_period")
    if st.button("Analyze risk", type="primary"):
        try:
            hist = get_history(ticker, period)
            metrics = calculate_risk(hist)
            if metrics.get("error"):
                st.warning(metrics["error"])
            else:
                cols = st.columns(4)
                cols[0].metric("Annualized volatility", f"{metrics['volatility']:.2%}")
                cols[1].metric("Max drawdown", f"{metrics['max_drawdown']:.2%}")
                cols[2].metric("Annualized return", f"{metrics['annual_return']:.2%}")
                cols[3].metric("Sharpe ratio*", f"{metrics['sharpe']:.2f}")
                st.line_chart(metrics["drawdown_series"])
                st.caption("*Sharpe ratio uses a zero risk-free-rate assumption. Historical risk measures are not guarantees.")
        except Exception as e:
            st.error(f"Risk analysis failed: {e}")

elif page == "Portfolio":
    st.title("Portfolio Tracker")
    with st.form("trade_form"):
        col1, col2, col3 = st.columns(3)
        ticker = col1.text_input("Ticker", "RELIANCE.NS").strip().upper()
        action = col2.selectbox("Transaction", ["BUY", "SELL"])
        quantity = col3.number_input("Quantity", min_value=0.0001, value=1.0, step=1.0)
        col4, col5 = st.columns(2)
        price = col4.number_input("Price per share", min_value=0.01, value=100.0, step=1.0)
        trade_date = col5.date_input("Trade date", value=date.today())
        note = st.text_input("Note (optional)")
        submitted = st.form_submit_button("Save transaction", type="primary")
    if submitted:
        ok, msg = add_trade(user_id, ticker, action, quantity, price, str(trade_date), note)
        (st.success if ok else st.error)(msg)
    trades = get_trades(user_id)
    if trades.empty:
        st.info("No transactions yet. Add BUY/SELL transactions above.")
    else:
        st.subheader("Transaction history")
        st.dataframe(trades, use_container_width=True)
        st.subheader("Current holdings & estimated P/L")
        holdings = []
        for t, group in trades.groupby("ticker"):
            qty = 0.0
            cost = 0.0
            for _, row in group.sort_values("trade_date").iterrows():
                q, p = float(row["quantity"]), float(row["price"])
                if row["action"] == "BUY":
                    cost += q * p
                    qty += q
                else:
                    avg = cost / qty if qty > 0 else 0
                    qty -= q
                    cost -= avg * q
            if qty > 0.0000001:
                try:
                    live = float(get_history(t, "5d")["Close"].iloc[-1])
                except Exception:
                    live = None
                holdings.append({"Ticker": t, "Quantity": round(qty, 4), "Avg cost": round(cost / qty, 2) if qty else 0,
                                 "Latest price": round(live, 2) if live else None,
                                 "Market value": round(qty * live, 2) if live else None,
                                 "Unrealized P/L": round(qty * live - cost, 2) if live else None})
        if holdings:
            hdf = pd.DataFrame(holdings)
            st.dataframe(hdf, use_container_width=True)
            if hdf["Market value"].notna().any():
                st.metric("Estimated portfolio market value", fmt_money(hdf["Market value"].sum(skipna=True)))
        with st.expander("Delete a transaction"):
            trade_ids = trades["id"].astype(int).tolist()
            chosen = st.selectbox("Transaction ID", trade_ids)
            if st.button("Delete selected transaction"):
                delete_trade(user_id, int(chosen))
                st.rerun()

elif page == "Watchlist":
    st.title("My Watchlist")
    with st.form("watch_add"):
        ticker = st.text_input("Ticker to add", "TCS.NS").strip().upper()
        add = st.form_submit_button("Add ticker")
    if add:
        ok, msg = add_watchlist(user_id, ticker)
        (st.success if ok else st.info)(msg)
    watch = get_watchlist(user_id)
    if watch:
        rows = []
        for t in watch:
            try:
                df = get_history(t, "5d")
                price = float(df["Close"].iloc[-1])
                change = (price / float(df["Close"].iloc[-2]) - 1) * 100 if len(df) > 1 else 0
                rows.append({"Ticker": t, "Latest close": price, "Daily change %": change})
            except Exception:
                rows.append({"Ticker": t, "Latest close": None, "Daily change %": None})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        remove = st.selectbox("Remove ticker", watch)
        if st.button("Remove from watchlist"):
            remove_watchlist(user_id, remove)
            st.rerun()
    else:
        st.info("Your watchlist is empty.")

elif page == "News Sentiment":
    st.title("Financial News Sentiment")
    ticker = get_ticker_input("news_ticker")
    if st.button("Fetch and score news", type="primary"):
        try:
            news = get_news(ticker)
            if not news:
                st.info("No news was returned by the data provider for this ticker.")
            else:
                scored = score_news(news)
                st.metric("Average headline sentiment", f"{scored['average']:+.2f}", scored["label"])
                st.caption("Lexicon-based headline sentiment is approximate; headlines may be incomplete or misclassified.")
                for item in scored["items"]:
                    with st.container(border=True):
                        st.write(f"**{item['title']}**")
                        st.caption(f"{item.get('publisher', 'Unknown publisher')} • Sentiment: {item['score']:+.2f} ({item['label']})")
                        if item.get("link"):
                            st.markdown(f"[Open article]({item['link']})")
        except Exception as e:
            st.error(f"News retrieval failed: {e}")

st.divider()
st.caption("Stock Analyzer Pro • Academic project • Not financial advice. Verify prices and fundamentals with official sources before acting.")
