"""
utils/loader.py
───────────────
Shared data loader with interactive (f)etch / (r)ead picker.
Works in both notebooks and scripts.
"""
from __future__ import annotations

import os

import pandas as pd

from .fetch import get_buy_data

CACHE = os.path.join("data", "df_raw.pkl")


def load_data() -> pd.DataFrame:
    has_cache = os.path.exists(CACHE)

    if has_cache:
        choice = ""
        while choice not in ("f", "r"):
            choice = input("  (f) Fetch fresh from API  or  (r) Read cached data?  → ").strip().lower()
    else:
        print("  No cache found — fetching from API.")
        choice = "f"

    if choice == "f":
        df_raw = get_buy_data(location="Detroit, MI", limit=200)
        os.makedirs("data", exist_ok=True)
        df_raw.to_pickle(CACHE)
        print(f"  Fetched {len(df_raw)} listings. Saved to cache.")
    else:
        df_raw = pd.read_pickle(CACHE)
        print(f"  Loaded {len(df_raw)} listings from cache.")

    return df_raw
