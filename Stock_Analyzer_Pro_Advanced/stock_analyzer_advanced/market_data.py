import streamlit as st
import yfinance as yf
import pandas as pd

@st.cache_data(ttl=300, show_spinner=False)
def get_history(ticker, period="1y", interval="1d"):
    ticker = ticker.strip().upper()
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False, threads=False)
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename_axis("Date")
    needed = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    df = df[needed].dropna(subset=["Close"])
    df.index = pd.to_datetime(df.index)
    return df

@st.cache_data(ttl=300, show_spinner=False)
def get_quote(ticker):
    info = yf.Ticker(ticker.strip().upper()).get_info()
    keep = ["longName", "currency", "sector", "industry", "marketCap", "trailingPE", "forwardPE", "trailingEps", "dividendYield", "website", "country"]
    return {k: info.get(k) for k in keep if info.get(k) is not None}

@st.cache_data(ttl=900, show_spinner=False)
def get_news(ticker):
    raw = yf.Ticker(ticker.strip().upper()).news or []
    items = []
    for item in raw[:15]:
        content = item.get("content") or {}
        title = content.get("title") or item.get("title") or ""
        canonical = content.get("canonicalUrl") or {}
        link = canonical.get("url") if isinstance(canonical, dict) else None
        if not link:
            link = item.get("link")
        provider = content.get("provider") or {}
        publisher = provider.get("displayName") if isinstance(provider, dict) else item.get("publisher")
        if title:
            items.append({"title": title, "link": link, "publisher": publisher or "Unknown"})
    return items
