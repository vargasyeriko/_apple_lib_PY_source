"""
utils/filters.py
────────────────
4-axis flip scoring + cluster assignment.

SCORING (0–10 scale):

  1. VALUE GAP (0–3)     price_per_sqft vs bedroom-group median
  2. DISTRESS (0–2)      foreclosure + price-reduced flags
  3. MARKET REJECTION (0–3)  relative DOM (days_on_market / avg)
  4. SELLER WEAKNESS (0–2)   price drop + stale combo

CLUSTERS:
  GOLD   — flip_score >= 4, sqft >= 1000, livable layout
  AVOID  — flip_score >= 4 but too small / cramped
  PASS   — flip_score < 4, no real upside

NOTE: The buy API has NO listing description text.
      Keyword matching ("fixer upper", "as-is") is not possible.
      Scoring uses every signal that IS available.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# ─── COLUMN MAPPING ──────────────────────────────────────────

_RENAME = {
    "list_price": "price",
    "description_sqft": "sqft",
    "description_beds": "beds",
    "description_baths_consolidated": "baths",
    "description_lot_sqft": "lot_sqft",
    "description_type": "prop_type",
    "description_sub_type": "sub_type",
    "location_address_line": "address",
    "location_address_city": "city",
    "location_address_postal_code": "zip",
    "location_address_coordinate_lat": "lat",
    "location_address_coordinate_lon": "lon",
    "location_county_name": "county",
    "flags_is_foreclosure": "is_foreclosure",
    "flags_is_price_reduced": "is_price_reduced",
    "price_reduced_amount": "price_reduced",
    "description_sold_price": "last_sold_price",
    "flags_is_pending": "is_pending",
    "flags_is_contingent": "is_contingent",
    "flags_is_new_listing": "is_new_listing",
    "permalink": "permalink",
    "primary_photo_href": "photo",
    "status": "status",
}

_NUMERIC = [
    "price", "sqft", "beds", "baths", "lot_sqft",
    "price_reduced", "last_sold_price", "lat", "lon",
]


def clean(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    rename = {k: v for k, v in _RENAME.items() if k in out.columns and v not in out.columns}
    out.rename(columns=rename, inplace=True)

    for c in _NUMERIC:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")

    if "list_date" in out.columns:
        out["list_date"] = pd.to_datetime(out["list_date"], errors="coerce", utc=True)
        out["days_on_market"] = (pd.Timestamp.now(tz="UTC") - out["list_date"]).dt.days

    if "price" in out.columns and "sqft" in out.columns:
        out["price_per_sqft"] = (out["price"] / out["sqft"].replace(0, np.nan)).round(1)

    if "sqft" in out.columns and "beds" in out.columns:
        out["sqft_per_bed"] = (out["sqft"] / out["beds"].replace(0, np.nan)).round(0)

    return out


# ─── INVESTMENT FILTER ────────────────────────────────────────

def investment_filter(
    df: pd.DataFrame,
    min_beds: int = 3,
    min_sqft: float = 1000,
    price_min: float = 60_000,
    price_max: float = 150_000,
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if "beds" in df.columns:
        mask &= df["beds"] >= min_beds
    if "sqft" in df.columns:
        mask &= df["sqft"] >= min_sqft
    if "price" in df.columns:
        mask &= df["price"].between(price_min, price_max)
    return df.loc[mask].reset_index(drop=True)


# ─── 4-AXIS FLIP SCORING ─────────────────────────────────────

def flip_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # --- AXIS 1: VALUE GAP (0–3) ---
    ax1 = pd.Series(0, index=out.index, dtype=int)
    if "price_per_sqft" in out.columns and "beds" in out.columns:
        med_ppsf = out.groupby("beds")["price_per_sqft"].transform("median")
        ratio = out["price_per_sqft"] / med_ppsf.replace(0, np.nan)
        ax1 = np.where(ratio < 0.60, 3,
               np.where(ratio < 0.75, 2,
               np.where(ratio < 0.90, 1, 0)))
        ax1 = pd.Series(ax1, index=out.index).fillna(0).astype(int)
        out["ppsf_vs_median"] = (ratio * 100).round(0).astype("Int64")
    out["ax_value_gap"] = ax1

    # --- AXIS 2: DISTRESS (0–2) ---
    ax2 = pd.Series(0, index=out.index, dtype=int)
    if "is_foreclosure" in out.columns:
        ax2 += out["is_foreclosure"].fillna(False).astype(bool).astype(int) * 2
    if "is_price_reduced" in out.columns:
        ax2 = ax2.clip(upper=0) + out["is_price_reduced"].fillna(False).astype(bool).astype(int)
        if "is_foreclosure" in out.columns:
            ax2 = (
                out["is_foreclosure"].fillna(False).astype(bool).astype(int) * 2
                + out["is_price_reduced"].fillna(False).astype(bool).astype(int)
            ).clip(upper=2)
    out["ax_distress"] = ax2

    # --- AXIS 3: MARKET REJECTION (0–3) ---
    ax3 = pd.Series(0, index=out.index, dtype=int)
    if "days_on_market" in out.columns:
        avg_dom = out["days_on_market"].mean()
        if avg_dom and avg_dom > 0:
            rel_dom = out["days_on_market"] / avg_dom
            ax3 = np.where(rel_dom > 2.0, 3,
                   np.where(rel_dom > 1.5, 2,
                   np.where(rel_dom > 1.0, 1, 0)))
            ax3 = pd.Series(ax3, index=out.index).fillna(0).astype(int)
            out["dom_vs_avg"] = (rel_dom * 100).round(0).astype("Int64")
    out["ax_market_reject"] = ax3

    # --- AXIS 4: SELLER WEAKNESS (0–2) ---
    ax4 = pd.Series(0, index=out.index, dtype=int)
    has_drop = out.get("is_price_reduced", pd.Series(False, index=out.index)).fillna(False).astype(bool)
    stale = out.get("days_on_market", pd.Series(0, index=out.index)).fillna(0) > 60
    ax4 = (has_drop & stale).astype(int) + (has_drop | stale).astype(int)
    ax4 = ax4.clip(upper=2)
    out["ax_seller_weak"] = ax4

    # --- TOTAL FLIP SCORE (0–10) ---
    out["flip_score"] = (
        out["ax_value_gap"]
        + out["ax_distress"]
        + out["ax_market_reject"]
        + out["ax_seller_weak"]
    )

    # --- CLUSTER ASSIGNMENT ---
    decent_structure = (
        out.get("sqft", pd.Series(0, index=out.index)).fillna(0) >= 1000
    ) & (
        out.get("sqft_per_bed", pd.Series(0, index=out.index)).fillna(0) >= 280
    )

    out["cluster"] = "PASS"
    out.loc[(out["flip_score"] >= 4) & decent_structure, "cluster"] = "GOLD"
    out.loc[(out["flip_score"] >= 4) & ~decent_structure, "cluster"] = "AVOID"

    return out
