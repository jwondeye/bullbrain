# performance_tracker.py — Evaluate Accuracy of Adaptive Bullish Scanner
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

def fetch_price_on_date(ticker, date):
    """Return close price for given date (or nearest trading day)."""
    try:
        df = yf.download(ticker, start=date - timedelta(days=2), end=date + timedelta(days=3), progress=False, auto_adjust=True)
        if df.empty: return None
        return df["Close"].iloc[-1]
    except:
        return None

def evaluate_performance(log_file="adaptive_bullish_log.csv"):
    try:
        log = pd.read_csv(log_file)
    except FileNotFoundError:
        print("❌ Log file not found. Run the bullish scanner first.")
        return

    log["Date"] = pd.to_datetime(log["Date"])
    results = []
    for _, row in log.iterrows():
        ticker, start_date, start_price = row["Ticker"], row["Date"], row["Price"]

        # Forward check dates
        for days in [1, 3, 5]:
            target_date = start_date + timedelta(days=days)
            end_price = fetch_price_on_date(ticker, target_date)
            if end_price is None:
                continue

            ret = (end_price - start_price) / start_price * 100
            results.append({
                "Ticker": ticker,
                "StartDate": start_date,
                "DaysAhead": days,
                "Return(%)": ret,
                "Regime": row["Regime"]
            })

    if not results:
        print("⚠️ No return data available (try after a few days of logs).")
        return

    df = pd.DataFrame(results)

    # Performance summary
    summary = (
        df.groupby("DaysAhead")["Return(%)"]
        .agg(["mean", lambda x: (x > 0).mean() * 100])
        .rename(columns={"<lambda_0>": "WinRate(%)"})
    )

    print("\n📊 Performance Summary (based on logged signals):")
    print(summary.round(2).to_string())
    print("\n--- Regime Breakdown ---")
    print(
        df.groupby(["Regime", "DaysAhead"])["Return(%)"]
        .agg(["mean", lambda x: (x > 0).mean() * 100])
        .rename(columns={"<lambda_0>": "WinRate(%)"})
        .round(2)
        .to_string()
    )

    print(f"\n✅ Evaluated {len(df)} signals from {log['Date'].min().date()} to {log['Date'].max().date()}.")

if __name__ == "__main__":
    print(f"\n📈 Adaptive Scanner Performance Tracker — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    evaluate_performance()
