import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

def add_indicators(df):
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    close = out["Close"].astype(float)
    out["SMA20"] = close.rolling(20).mean()
    out["SMA50"] = close.rolling(50).mean()
    out["EMA12"] = close.ewm(span=12, adjust=False).mean()
    out["EMA26"] = close.ewm(span=26, adjust=False).mean()
    out["MACD"] = out["EMA12"] - out["EMA26"]
    out["MACD_signal"] = out["MACD"].ewm(span=9, adjust=False).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    out["RSI"] = 100 - (100 / (1 + rs))
    rolling_std = close.rolling(20).std()
    out["BB_upper"] = out["SMA20"] + 2 * rolling_std
    out["BB_lower"] = out["SMA20"] - 2 * rolling_std
    out["DailyReturn"] = close.pct_change()
    return out

def calculate_risk(df):
    if df is None or len(df) < 3:
        return {"error": "At least 3 price observations are required."}
    close = df["Close"].dropna().astype(float)
    returns = close.pct_change().dropna()
    if len(returns) < 2:
        return {"error": "Not enough returns to calculate risk."}
    vol = float(returns.std(ddof=1) * np.sqrt(252))
    annual_return = float((close.iloc[-1] / close.iloc[0]) ** (252 / max(len(returns), 1)) - 1) if close.iloc[0] > 0 else 0.0
    wealth = (1 + returns).cumprod()
    peak = wealth.cummax()
    drawdown = wealth / peak - 1
    sharpe = float((returns.mean() / returns.std(ddof=1)) * np.sqrt(252)) if returns.std(ddof=1) else 0.0
    return {"volatility": vol, "annual_return": annual_return, "max_drawdown": float(drawdown.min()),
            "sharpe": sharpe, "drawdown_series": drawdown}

def _features(close):
    data = pd.DataFrame({"close": close.astype(float)})
    for lag in range(1, 11):
        data[f"lag_{lag}"] = data["close"].shift(lag)
    data["return_1"] = data["close"].pct_change()
    data["sma5"] = data["close"].rolling(5).mean()
    data["sma10"] = data["close"].rolling(10).mean()
    data["volatility10"] = data["return_1"].rolling(10).std()
    data["target"] = data["close"].shift(-1)
    return data.dropna()

def predict_next_close(df):
    if df is None or df.empty or len(df) < 80:
        return {"error": "At least 80 daily observations are recommended. Select 1y or longer history."}
    close = df["Close"].dropna()
    data = _features(close)
    if len(data) < 40:
        return {"error": "Not enough clean data after feature preparation."}
    feature_cols = [c for c in data.columns if c not in ("close", "target")]
    split = int(len(data) * 0.8)
    train, test = data.iloc[:split], data.iloc[split:]
    model = RandomForestRegressor(n_estimators=250, max_depth=8, min_samples_leaf=2, random_state=42, n_jobs=-1)
    model.fit(train[feature_cols], train["target"])
    pred = model.predict(test[feature_cols])
    mae = float(mean_absolute_error(test["target"], pred))
    latest_features = data.iloc[[-1]][feature_cols]
    next_pred = float(model.predict(latest_features)[0])
    return {"prediction": next_pred, "last_close": float(close.iloc[-1]), "mae": mae,
            "actual": test["target"].reset_index(drop=True), "predicted": pd.Series(pred),
            "model": "Random Forest Regressor (time-ordered holdout)"}

def compare_performance(tickers, period="1y"):
    import yfinance as yf
    data = yf.download(tickers, period=period, auto_adjust=True, progress=False, threads=False)
    if data is None or data.empty:
        return pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        if "Close" not in data.columns.get_level_values(0):
            return pd.DataFrame()
        closes = data["Close"]
    else:
        closes = data[["Close"]].rename(columns={"Close": tickers[0]})
    normalized = closes.dropna(how="all")
    normalized = normalized.apply(lambda s: s / s.dropna().iloc[0] * 100 if s.notna().any() else s)
    return normalized
