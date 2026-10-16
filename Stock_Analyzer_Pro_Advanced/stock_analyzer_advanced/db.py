import sqlite3
import hashlib
import os
import hmac
from pathlib import Path

DB_PATH = Path(os.getenv("STOCK_ANALYZER_DB", "stock_analyzer.db"))

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            ticker TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, ticker)
        );
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            ticker TEXT NOT NULL,
            action TEXT NOT NULL CHECK(action IN ('BUY','SELL')),
            quantity REAL NOT NULL CHECK(quantity > 0),
            price REAL NOT NULL CHECK(price > 0),
            trade_date TEXT NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist(user_id);
        CREATE INDEX IF NOT EXISTS idx_trades_user ON trades(user_id);
        """)
        conn.commit()

def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 260000).hex()

def create_user(username, email, password):
    salt = os.urandom(16).hex()
    hashed = _hash_password(password, salt)
    try:
        with connect() as conn:
            conn.execute("INSERT INTO users(username,email,password_hash,salt) VALUES(?,?,?,?)",
                         (username, email or None, hashed, salt))
            conn.commit()
        return True, "Account created. You can now log in."
    except sqlite3.IntegrityError:
        return False, "That username already exists."

def authenticate_user(username, password):
    with connect() as conn:
        row = conn.execute("SELECT id,username,role,password_hash,salt FROM users WHERE username=?",
                           (username,)).fetchone()
    if not row:
        return None
    candidate = _hash_password(password, row["salt"])
    if hmac.compare_digest(candidate, row["password_hash"]):
        return (row["id"], row["username"], row["role"])
    return None

def add_watchlist(user_id, ticker):
    ticker = ticker.strip().upper()
    if not ticker or len(ticker) > 30 or any(ch.isspace() for ch in ticker):
        return False, "Enter a valid ticker symbol."
    try:
        with connect() as conn:
            conn.execute("INSERT INTO watchlist(user_id,ticker) VALUES(?,?)", (user_id, ticker))
            conn.commit()
        return True, f"{ticker} added to watchlist."
    except sqlite3.IntegrityError:
        return False, f"{ticker} is already in your watchlist."

def get_watchlist(user_id):
    with connect() as conn:
        rows = conn.execute("SELECT ticker FROM watchlist WHERE user_id=? ORDER BY ticker", (user_id,)).fetchall()
    return [r["ticker"] for r in rows]

def remove_watchlist(user_id, ticker):
    with connect() as conn:
        conn.execute("DELETE FROM watchlist WHERE user_id=? AND ticker=?", (user_id, ticker))
        conn.commit()

def add_trade(user_id, ticker, action, quantity, price, trade_date, note=""):
    ticker = ticker.strip().upper()
    if not ticker or len(ticker) > 30:
        return False, "Enter a valid ticker."
    if quantity <= 0 or price <= 0:
        return False, "Quantity and price must be greater than zero."
    with connect() as conn:
        if action == "SELL":
            rows = conn.execute("SELECT action,quantity FROM trades WHERE user_id=? AND ticker=? ORDER BY trade_date,id",
                                 (user_id, ticker)).fetchall()
            held = sum(r["quantity"] if r["action"] == "BUY" else -r["quantity"] for r in rows)
            if quantity > held + 1e-8:
                return False, f"Cannot sell {quantity:g}; recorded holdings are {held:g}."
        conn.execute("""INSERT INTO trades(user_id,ticker,action,quantity,price,trade_date,note)
                        VALUES(?,?,?,?,?,?,?)""",
                     (user_id, ticker, action, quantity, price, trade_date, note))
        conn.commit()
    return True, "Transaction saved."

def get_trades(user_id):
    import pandas as pd
    with connect() as conn:
        rows = conn.execute("""SELECT id,ticker,action,quantity,price,trade_date,note
                               FROM trades WHERE user_id=? ORDER BY trade_date DESC,id DESC""", (user_id,)).fetchall()
    return pd.DataFrame([dict(r) for r in rows])

def delete_trade(user_id, trade_id):
    with connect() as conn:
        conn.execute("DELETE FROM trades WHERE user_id=? AND id=?", (user_id, trade_id))
        conn.commit()
