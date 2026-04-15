"""
utils/fetch.py
──────────────
Hit the Realtor16 RapidAPI and return a clean DataFrame of for-sale listings.
"""
from __future__ import annotations

import pandas as pd
import requests

API_KEY = "e8ed9c0c93msh606b92a16b58a9cp187683jsn253baf6dc2f5"

_URL = "https://realtor16.p.rapidapi.com/search/forsale"
_HOST = "realtor16.p.rapidapi.com"


def _flatten(d, parent_key="", sep="_"):
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            new = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(_flatten(v, new, sep).items())
    elif isinstance(d, list):
        if d:
            items.extend(_flatten(d[0], parent_key, sep).items())
    else:
        items.append((parent_key, d))
    return dict(items)


def get_buy_data(location: str = "Detroit, MI", limit: int = 200) -> pd.DataFrame:
    headers = {
        "X-RapidAPI-Key": API_KEY.strip(),
        "X-RapidAPI-Host": _HOST,
    }
    params = {"location": location, "limit": limit}

    resp = requests.get(_URL, headers=headers, params=params, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"API {resp.status_code}: {resp.text[:300]}")

    listings = resp.json().get("properties", [])
    if not listings:
        return pd.DataFrame()

    return pd.DataFrame([_flatten(p) for p in listings])
