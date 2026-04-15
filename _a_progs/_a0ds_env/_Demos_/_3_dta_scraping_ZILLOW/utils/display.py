"""
utils/display.py
────────────────
Minimal investor-focused output.
"""
from __future__ import annotations

import pandas as pd


def _fp(v):
    if pd.isna(v):
        return "—"
    if v >= 1_000_000:
        return f"${v / 1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v / 1_000:.0f}K"
    return f"${v:.0f}"


# The only columns a client needs to see
_COLS = [
    "address", "city", "zip",
    "price", "beds", "baths", "sqft", "price_per_sqft",
    "days_on_market", "flip_score", "cluster",
]


def picks_table(df: pd.DataFrame, n: int | None = None) -> pd.DataFrame:
    cols = [c for c in _COLS if c in df.columns]
    out = df[cols].copy()

    if "price" in out.columns:
        out["price"] = df["price"].apply(_fp)
    if "price_per_sqft" in out.columns:
        out["price_per_sqft"] = df["price_per_sqft"].apply(
            lambda v: f"${v:,.0f}" if pd.notna(v) else "—"
        )
    if "days_on_market" in out.columns:
        out["days_on_market"] = df["days_on_market"].fillna(0).astype(int)

    if "flip_score" in df.columns:
        out = out.sort_values("flip_score", ascending=False)

    if n:
        out = out.head(n)
    return out.reset_index(drop=True)


def quick_stats(df: pd.DataFrame) -> str:
    lines = [f"  {len(df)} properties"]
    if "price" in df.columns:
        p = df["price"].dropna()
        if not p.empty:
            lines.append(f"  Price range   {_fp(p.min())} – {_fp(p.max())}  (median {_fp(p.median())})")
    if "price_per_sqft" in df.columns:
        ppsf = df["price_per_sqft"].dropna()
        if not ppsf.empty:
            lines.append(f"  Median $/sqft ${ppsf.median():,.0f}")
    if "days_on_market" in df.columns:
        dom = df["days_on_market"].dropna()
        if not dom.empty:
            lines.append(f"  Avg DOM       {dom.mean():.0f} days")
    if "cluster" in df.columns:
        gold = (df["cluster"] == "GOLD").sum()
        lines.append(f"  GOLD picks    {gold}")
    return "\n".join(lines)
