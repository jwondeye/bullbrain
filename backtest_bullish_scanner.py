# backtest_bullish_scanner.py — Accuracy-Optimized Version + Charting
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import logging
logging.getLogger("yfinance").setLevel(logging.CRITICAL)


def download_clean_data(ticker, start="2018-01-01", end=None):
    """Download and flatten MultiIndex yfinance data."""
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    df = yf.download(ticker, start=start, end=end, interval="1d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    df.columns = [c.lower() for c in df.columns]
    df = df[["close", "volume"]].dropna(subset=["close"])
    return df


def compute_indicators(df):
    """Compute key technical indicators."""
    df["SMA5"] = df["close"].rolling(5).mean()
    df["SMA20"] = df["close"].rolling(20).mean()
    df["EMA10"] = df["close"].ewm(span=10, adjust=False).mean()
    df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(span=14, min_periods=14).mean()
    avg_loss = loss.ewm(span=14, min_periods=14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))

    # Volume
    df["Vol_MA5"] = df["volume"].rolling(5).mean()

    # Momentum
    df["Momentum"] = df["close"].diff(3)

    df.dropna(inplace=True)
    return df


def generate_signals(df):
    """Generate stronger bullish signals."""
    df["Signal"] = (
        (df["EMA10"] > df["EMA20"]) &
        (df["SMA5"] > df["SMA20"]) &
        (df["RSI"].between(50, 65)) &
        (df["Momentum"] > 0) &
        (df["volume"] > df["Vol_MA5"])
    )
    return df


def backtest_ticker(ticker):
    """Backtest one ticker with improved signal logic."""
    df = download_clean_data(ticker)
    if df.empty:
        return None

    df = compute_indicators(df)
    df = generate_signals(df)

    df["Next_Close"] = df["close"].shift(-1)
    df["Next_Return"] = df["Next_Close"] / df["close"] - 1
    df.dropna(inplace=True)

    signals = df[df["Signal"]]
    if signals.empty:
        return None

    avg_return = signals["Next_Return"].mean()
    win_rate = (signals["Next_Return"] > 0).mean()
    total_signals = len(signals)

    return {
        "Ticker": ticker,
        "Signals": total_signals,
        "WinRate": win_rate,
        "AvgReturn": avg_return,
        "Data": df,
    }


def plot_signals(ticker, df):
    """Visualize signals for one ticker."""
    plt.figure(figsize=(12,6))
    plt.plot(df.index, df["close"], label="Close", color="blue", alpha=0.6)
    plt.plot(df.index, df["SMA5"], label="SMA5", color="orange", alpha=0.8)
    plt.plot(df.index, df["SMA20"], label="SMA20", color="red", alpha=0.8)
    buy_signals = df[df["Signal"]]
    plt.scatter(buy_signals.index, buy_signals["close"], color="green", marker="^", s=80, label="Bullish Signal")
    plt.title(f"Bullish Signals for {ticker}")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    sp_tickers = ["AAPL","MSFT","NVDA","AMZN","META","GOOGL",
                  "TSLA","JPM","AMD","NFLX","KO","PEP","V","MA","XOM","UNH"]

    print(f"\n📊 Backtesting Bullish Scanner (Optimized) — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    results = []
    for t in sp_tickers:
        try:
            res = backtest_ticker(t)
            if res:
                results.append(res)
                print(f"{t} ✅ Signals: {res['Signals']} | WinRate: {res['WinRate']:.1%} | AvgReturn: {res['AvgReturn']*100:.2f}%")
            else:
                print(f"{t} ⚠️ No signals found.")
        except Exception as e:
            print(f"{t} ❌ Error: {e}")

    if results:
        df_res = pd.DataFrame(results)[["Ticker", "Signals", "WinRate", "AvgReturn"]]
        print("\n--- Summary ---")
        print(df_res.sort_values("WinRate", ascending=False).to_string(index=False, formatters={
            "WinRate": "{:.1%}".format,
            "AvgReturn": lambda x: f"{x*100:.2f}%"
        }))
        print("\n✅ Backtest complete! Fewer but stronger signals.\n")

        # Optional visualization
        ticker_choice = input("Enter a ticker to visualize (or press Enter to skip): ").strip().upper()
        if ticker_choice and ticker_choice in [r["Ticker"] for r in results]:
            df_data = next(r["Data"] for r in results if r["Ticker"] == ticker_choice)
            plot_signals(ticker_choice, df_data)
    else:
        print("❌ No valid data retrieved. Try again later.")
