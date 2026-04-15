"""
app.py — Stock Analysis Terminal Dashboard
===========================================
Run:   python3 app.py
       python3 app.py TSLA
       python3 app.py NVDA AMD TSM ASML
"""

import sys
import yfinance as yf

from function_fin import (
    volatility_trend,
    momentum_decay,
    support_resistance,
    regime_detector,
    breakout_pressure,
    risk_map,
    correlation_cluster,
    mean_reversion,
    smart_money,
    decision_engine,
)


# ######################################################################
#  CONFIGURATION
# ######################################################################

DEFAULT_TICKER = "NVDA"
DEFAULT_PEERS  = ["AMD", "TSM", "ASML"]
DATA_PERIOD    = "1y"


# ######################################################################
#  DATA FETCH
# ######################################################################

def fetch(ticker, period=DATA_PERIOD):
    """Download OHLCV from Yahoo Finance."""
    df = yf.download(ticker, period=period, progress=False)
    if hasattr(df.columns, "levels") and df.columns.nlevels > 1:
        df.columns = df.columns.droplevel(1)
    return df


# ######################################################################
#  MAIN
# ######################################################################

def main():
    tickers = sys.argv[1:] if len(sys.argv) > 1 else [DEFAULT_TICKER]
    ticker = tickers[0]
    peers = tickers[1:] if len(tickers) > 1 else DEFAULT_PEERS

    print()
    print("  ╔══════════════════════════════════════════════╗")
    print(f"  ║   STOCK ANALYSIS DASHBOARD — {ticker:<16} ║")
    print("  ╚══════════════════════════════════════════════╝")

    print(f"\n  Fetching {ticker} data...")
    df = fetch(ticker)
    if df.empty:
        print(f"  ERROR: No data for {ticker}")
        return

    print(f"  Got {len(df)} bars  ({df.index[0].date()} → {df.index[-1].date()})")

    # ── Run all 10 analyses ──────────────────────────────

    print("\n  ┌─────────────────────────────────────────────┐")
    print("  │  1/10  VOLATILITY + TREND COMPRESSION       │")
    print("  └─────────────────────────────────────────────┘")
    volatility_trend(df, ticker)

    print("  ┌─────────────────────────────────────────────┐")
    print("  │  2/10  MOMENTUM DECAY RADAR                 │")
    print("  └─────────────────────────────────────────────┘")
    momentum_decay(df, ticker)

    print("  ┌─────────────────────────────────────────────┐")
    print("  │  3/10  SUPPORT / RESISTANCE HEATMAP         │")
    print("  └─────────────────────────────────────────────┘")
    support_resistance(df, ticker)

    print("  ┌─────────────────────────────────────────────┐")
    print("  │  4/10  REGIME DETECTOR                      │")
    print("  └─────────────────────────────────────────────┘")
    regime_detector(df, ticker)

    print("  ┌─────────────────────────────────────────────┐")
    print("  │  5/10  BREAKOUT PRESSURE GAUGE              │")
    print("  └─────────────────────────────────────────────┘")
    breakout_pressure(df, ticker)

    print("  ┌─────────────────────────────────────────────┐")
    print("  │  6/10  RISK MAP                             │")
    print("  └─────────────────────────────────────────────┘")
    risk_map(df, ticker)

    print("  ┌─────────────────────────────────────────────┐")
    print("  │  7/10  CORRELATION CLUSTER                  │")
    print("  └─────────────────────────────────────────────┘")
    print(f"  Fetching peers: {', '.join(peers)}...")
    df_dict = {ticker: df}
    for p in peers:
        pdf = fetch(p)
        if not pdf.empty:
            df_dict[p] = pdf
    correlation_cluster(df_dict, ticker, peers)

    print("  ┌─────────────────────────────────────────────┐")
    print("  │  8/10  MEAN REVERSION SIGNAL                │")
    print("  └─────────────────────────────────────────────┘")
    mean_reversion(df, ticker)

    print("  ┌─────────────────────────────────────────────┐")
    print("  │  9/10  SMART MONEY TRACKER                  │")
    print("  └─────────────────────────────────────────────┘")
    smart_money(df, ticker)

    print("  ┌─────────────────────────────────────────────┐")
    print("  │  10/10 DECISION ENGINE                      │")
    print("  └─────────────────────────────────────────────┘")
    decision_engine(df, ticker)

    print("  Done.\n")


if __name__ == "__main__":
    main()
