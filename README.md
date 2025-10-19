# 📈 Adaptive Bullish Signal Scanner

A Python-based quantitative trading project that identifies **short-term bullish signals** across major equities using technical indicators and adaptive market regimes.

---

## 🚀 Features
- Analyzes stocks using indicators such as **RSI**, **moving averages**, **momentum**, and **volume strength**  
- Detects **market regime shifts** (Calm, Volatile, or Sideways) to adapt strategy dynamically  
- Produces a ranked list of top 5 stocks with the **strongest bullish potential** each day  
- Includes a **backtesting module** that evaluates performance accuracy over historical data  
- Automatically logs results for consistent tracking and review  

---

## 🧠 Technical Overview
This scanner uses:
- **yfinance** for live & historical price data  
- **pandas / numpy** for data analysis and calculations  
- A weighted **bullish scoring system** that considers:
  - SMA/EMA crossovers  
  - RSI momentum confirmation  
  - Volume spikes  
  - Market volatility normalization  
  - Relative strength vs. SPY  

---

## 📊 Example Output
📈 Adaptive Bullish Scanner — 2025-10-19 15:07

GOOGL Score: 65 Price: $253.30 Regime: Calm

KO Score: 65 Price: $68.44 Regime: Calm

AAPL Score: 60 Price: $252.29 Regime: Calm

TSLA Score: 50 Price: $439.31 Regime: Volatile

AMD Score: 50 Price: $233.08 Regime: Volatile

✅ Adaptive Top 5 bullish signals saved and logged.

## 🧑‍💻 Author
**Jericho Wondeye**  
📍 University of Maryland — Computer Engineering, Business Scholars Program  
📧 [jwondeye@terpmail.umd.edu]  


