#!/usr/bin/env python3
"""
run.py — Detroit Flip Scanner
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from utils import load_data, clean, investment_filter, flip_score
from utils.display import picks_table, quick_stats


def main():
    print("\n══════════════════════════════════════════════")
    print("  DETROIT FLIP SCANNER")
    print("══════════════════════════════════════════════")

    df_raw = load_data()
    df = flip_score(clean(df_raw))
    df_inv = flip_score(investment_filter(df, min_beds=3, min_sqft=1000,
                                          price_min=60_000, price_max=150_000))
    gold = df_inv[df_inv["cluster"] == "GOLD"]

    print("\n──────────────────────────────────────────────")
    print("  MARKET")
    print("──────────────────────────────────────────────")
    print(quick_stats(df))

    print(f"\n──────────────────────────────────────────────")
    print(f"  FILTERED  ({len(df_inv)} match)")
    print("  3+ beds · 1000+ sqft · $60K–$150K")
    print("──────────────────────────────────────────────")
    print(quick_stats(df_inv))

    if not gold.empty:
        print(f"\n──────────────────────────────────────────────")
        print(f"  GOLD PICKS  ({len(gold)})")
        print("──────────────────────────────────────────────")
        print(picks_table(gold).to_string(index=False))

    print(f"\n──────────────────────────────────────────────")
    print(f"  ALL FILTERED (ranked)")
    print("──────────────────────────────────────────────")
    print(picks_table(df_inv).to_string(index=False))

    os.makedirs("data", exist_ok=True)
    df_inv.to_pickle("data/df_picks.pkl")
    print(f"\n  Saved → data/df_picks.pkl ({len(df_inv)} rows)\n")


if __name__ == "__main__":
    main()
