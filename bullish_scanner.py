# bullish_scanner.py — Adaptive Bullish Scanner with Auto Logging
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# ----------------------------
# 🔹 DATA COLLECTION
# ----------------------------
def download_data(ticker, period="3mo", interval="1d"):
    df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df[["Close", "Volume"]].dropna()
    return df

# ----------------------------
# 🔹 INDICATOR CALCULATIONS
# ----------------------------
def compute_indicators(df):
    df["SMA5"] = df["Close"].rolling(5).mean()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["EMA10"] = df["Close"].ewm(span=10, adjust=False).mean()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(span=14, min_periods=14).mean()
    avg_loss = loss.ewm(span=14, min_periods=14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))

    df["Volatility"] = df["Close"].pct_change().rolling(10).std()
    df["Volume_MA5"] = df["Volume"].rolling(5).mean()
    df["Momentum"] = df["Close"].diff(3)
    df.dropna(inplace=True)
    return df

# ----------------------------
# 🔹 ADAPTIVE SCORING SYSTEM
# ----------------------------
def adaptive_scoring(df, spy_df):
    """Adaptive bullish scoring system based on volatility regime."""
    latest = df.iloc[-1]
    vol = df["Volatility"].iloc[-10:].mean()

    # Adaptive RSI thresholds
    if vol < 0.015:
        rsi_min, rsi_max = 52, 64
        regime = "Calm"
    elif vol < 0.03:
        rsi_min, rsi_max = 50, 66
        regime = "Moderate"
    else:
        rsi_min, rsi_max = 48, 70
        regime = "Volatile"

    # Volume threshold adapts with volatility
    volume_ratio_threshold = 1.1 if vol < 0.02 else 1.3

    # Momentum z-score
    df["Momentum_Z"] = (df["Momentum"] - df["Momentum"].rolling(20).mean()) / (df["Momentum"].rolling(20).std() + 1e-9)
    latest_mom_z = df["Momentum_Z"].iloc[-1]

    # Market-relative strength
    stock_ret = df["Close"].pct_change(5).iloc[-1]
    spy_ret = spy_df["Close"].pct_change(5).iloc[-1]
    rel_strength = stock_ret - spy_ret

    score = 0
    if latest["EMA10"] > latest["EMA20"]:
        score += 15
    if latest["SMA5"] > latest["SMA20"]:
        score += 15
    if rsi_min <= latest["RSI"] <= rsi_max:
        score += 10
    if latest["Volume"] > latest["Volume_MA5"] * volume_ratio_threshold:
        score += 10
    if latest_mom_z > 0:
        score += 10
    if rel_strength > 0:
        score += 10
    if latest["Volatility"] < 0.05:
        score += 5
    if latest["RSI"] > 75:
        score -= 10

    return max(0, min(100, score)), regime

# ----------------------------
# 🔹 SCAN MULTIPLE STOCKS
# ----------------------------
def scan_stocks(tickers):
    spy_df = download_data("SPY")
    results = []
    for t in tickers:
        try:
            df = download_data(t)
            df = compute_indicators(df)
            score, regime = adaptive_scoring(df, spy_df)
            price = df["Close"].iloc[-1]
            results.append((t, score, price, regime))
        except Exception as e:
            print(f"Skipping {t}: {e}")
    ranked = sorted(results, key=lambda x: x[1], reverse=True)
    return ranked

# ----------------------------
# 🔹 AUTO-LOGGING RESULTS
# ----------------------------
def log_results(top_stocks):
    log_file = "adaptive_bullish_log.csv"
    now = datetime.now().strftime("%Y-%m-%d")
    data = []
    for t, score, price, regime in top_stocks:
        data.append({
            "Date": now,
            "Ticker": t,
            "Score": score,
            "Price": price,
            "Regime": regime
        })
    df = pd.DataFrame(data)

    if os.path.exists(log_file):
        df.to_csv(log_file, mode="a", header=False, index=False)
    else:
        df.to_csv(log_file, index=False)
    print(f"\n💾 Logged results for {now} in {log_file}")

# ----------------------------
# 🔹 MAIN EXECUTION
# ----------------------------
if __name__ == "__main__":
    sp_tickers = ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","JPM","AMD","NFLX","KO","PEP","V","MA","XOM","UNH"]
    print(f"\n📈 Adaptive Bullish Scanner — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    ranked = scan_stocks(sp_tickers)

    if ranked:
        top = ranked[:5]
        for i, (ticker, score, price, regime) in enumerate(top, start=1):
            print(f"{i}. {ticker:5s}  Score: {score:3d}  Price: ${price:,.2f}  Regime: {regime}")
        log_results(top)
        print("\n✅ Adaptive Top 5 bullish signals saved and logged.\n")
    else:
        print("⚠️ No valid data retrieved.")
