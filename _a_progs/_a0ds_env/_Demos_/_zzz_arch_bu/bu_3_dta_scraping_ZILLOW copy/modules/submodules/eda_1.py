from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

CHARTS_DIR = Path("data") / "charts"
HTML_OUT = "detroit_real_estate_insights.html"

COL_MAP = {
    "list_price": "price",
    "description_sqft": "sqft",
    "description_lot_sqft": "lot_sqft",
    "description_beds": "beds",
    "description_baths_consolidated": "baths",
    "description_type": "prop_type",
    "location_address_line": "address",
    "location_address_city": "city",
    "location_county_name": "county",
    "price_reduced_amount": "price_reduced",
    "flags_is_price_reduced": "is_price_reduced",
    "flags_is_new_listing": "is_new_listing",
    "flags_is_pending": "is_pending",
    "flags_is_foreclosure": "is_foreclosure",
    "flags_is_contingent": "is_contingent",
}

PLT_STYLE = {
    "figure.facecolor": "#0e1117",
    "axes.facecolor": "#161b22",
    "axes.edgecolor": "#30363d",
    "axes.labelcolor": "#c9d1d9",
    "text.color": "#c9d1d9",
    "xtick.color": "#8b949e",
    "ytick.color": "#8b949e",
    "grid.color": "#21262d",
    "grid.alpha": 0.6,
    "font.family": "sans-serif",
    "font.size": 11,
}

ACCENT = "#58a6ff"
GREEN = "#3fb950"
RED = "#f85149"
YELLOW = "#d29922"
PURPLE = "#bc8cff"
PALETTE = ["#58a6ff", "#3fb950", "#d29922", "#f85149", "#bc8cff", "#79c0ff", "#f0883e"]


def _prep(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    rename = {k: v for k, v in COL_MAP.items() if k in out.columns and v not in out.columns}
    out.rename(columns=rename, inplace=True)

    for c in ("price", "sqft", "lot_sqft", "beds", "baths", "price_reduced"):
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")

    if "list_date" in out.columns:
        out["list_date"] = pd.to_datetime(out["list_date"], errors="coerce", utc=True)
        out["days_on_market"] = (pd.Timestamp.now(tz="UTC") - out["list_date"]).dt.days

    if "price" in out.columns and "sqft" in out.columns:
        out["price_per_sqft"] = out["price"] / out["sqft"].replace(0, np.nan)

    if "price_reduced" in out.columns and "price" in out.columns:
        out["discount_pct"] = (out["price_reduced"] / (out["price"] + out["price_reduced"])) * 100

    return out


def _save_fig(fig: plt.Figure, name: str) -> Path:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = CHARTS_DIR / f"{name}.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def _fmt_price(x, _=None):
    if x >= 1_000_000:
        return f"${x / 1_000_000:.1f}M"
    if x >= 1_000:
        return f"${x / 1_000:.0f}K"
    return f"${x:.0f}"


# ─── CHART BUILDERS ───────────────────────────────────────────


def _chart_price_distribution(df: pd.DataFrame) -> Path | None:
    prices = df["price"].dropna()
    if prices.empty:
        return None
    with plt.rc_context(PLT_STYLE):
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.hist(prices, bins=30, color=ACCENT, edgecolor="#0e1117", alpha=0.85)
        ax.axvline(prices.median(), color=YELLOW, ls="--", lw=1.5, label=f"Median {_fmt_price(prices.median())}")
        ax.axvline(prices.mean(), color=RED, ls="--", lw=1.5, label=f"Mean {_fmt_price(prices.mean())}")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(_fmt_price))
        ax.set_xlabel("List Price")
        ax.set_ylabel("Count")
        ax.set_title("Price Distribution", fontsize=14, fontweight="bold", color="white")
        ax.legend(facecolor="#161b22", edgecolor="#30363d")
        ax.grid(axis="y")
    return _save_fig(fig, "price_distribution")


def _chart_price_per_sqft(df: pd.DataFrame) -> Path | None:
    sub = df.dropna(subset=["price_per_sqft"])
    if sub.empty:
        return None
    with plt.rc_context(PLT_STYLE):
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.hist(sub["price_per_sqft"], bins=30, color=GREEN, edgecolor="#0e1117", alpha=0.85)
        med = sub["price_per_sqft"].median()
        ax.axvline(med, color=YELLOW, ls="--", lw=1.5, label=f"Median ${med:,.0f}/sqft")
        ax.set_xlabel("Price / sqft ($)")
        ax.set_ylabel("Count")
        ax.set_title("Price per Sqft", fontsize=14, fontweight="bold", color="white")
        ax.legend(facecolor="#161b22", edgecolor="#30363d")
        ax.grid(axis="y")
    return _save_fig(fig, "price_per_sqft")


def _chart_price_vs_sqft(df: pd.DataFrame) -> Path | None:
    sub = df.dropna(subset=["price", "sqft"])
    if sub.empty:
        return None
    with plt.rc_context(PLT_STYLE):
        fig, ax = plt.subplots(figsize=(10, 5.5))
        sc = ax.scatter(sub["sqft"], sub["price"], c=sub.get("days_on_market", pd.Series(dtype=float)),
                        cmap="RdYlGn", s=50, alpha=0.8, edgecolors="#30363d", linewidths=0.4)
        if "days_on_market" in sub.columns and sub["days_on_market"].notna().any():
            cbar = fig.colorbar(sc, ax=ax, pad=0.02)
            cbar.set_label("Days on Market", color="#c9d1d9")
            cbar.ax.yaxis.set_tick_params(color="#8b949e")
            plt.setp(plt.getp(cbar.ax, "yticklabels"), color="#8b949e")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_price))
        ax.set_xlabel("Sqft")
        ax.set_ylabel("Price")
        ax.set_title("Price vs Sqft  (color = days on market)", fontsize=14, fontweight="bold", color="white")
        ax.grid(True, alpha=0.3)
    return _save_fig(fig, "price_vs_sqft")


def _chart_beds_price_box(df: pd.DataFrame) -> Path | None:
    sub = df.dropna(subset=["beds", "price"])
    sub = sub[sub["beds"].between(1, 8)]
    if sub.empty:
        return None
    with plt.rc_context(PLT_STYLE):
        fig, ax = plt.subplots(figsize=(10, 4.5))
        groups = [g["price"].values for _, g in sub.groupby("beds")]
        labels = [str(int(b)) for b in sorted(sub["beds"].unique())]
        bp = ax.boxplot(groups, labels=labels, patch_artist=True, widths=0.5,
                        medianprops=dict(color=YELLOW, lw=2),
                        flierprops=dict(marker="o", markerfacecolor=RED, markersize=4, alpha=0.5))
        for patch, c in zip(bp["boxes"], PALETTE * 3):
            patch.set_facecolor(c)
            patch.set_alpha(0.7)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_price))
        ax.set_xlabel("Bedrooms")
        ax.set_ylabel("Price")
        ax.set_title("Price by Bedroom Count", fontsize=14, fontweight="bold", color="white")
        ax.grid(axis="y")
    return _save_fig(fig, "beds_price_box")


def _chart_dom_distribution(df: pd.DataFrame) -> Path | None:
    dom = df["days_on_market"].dropna()
    if dom.empty:
        return None
    with plt.rc_context(PLT_STYLE):
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.hist(dom, bins=25, color=PURPLE, edgecolor="#0e1117", alpha=0.85)
        ax.axvline(dom.median(), color=YELLOW, ls="--", lw=1.5, label=f"Median {dom.median():.0f} days")
        ax.set_xlabel("Days on Market")
        ax.set_ylabel("Count")
        ax.set_title("Days on Market Distribution", fontsize=14, fontweight="bold", color="white")
        ax.legend(facecolor="#161b22", edgecolor="#30363d")
        ax.grid(axis="y")
    return _save_fig(fig, "dom_distribution")


def _chart_type_breakdown(df: pd.DataFrame) -> Path | None:
    if "prop_type" not in df.columns:
        return None
    counts = df["prop_type"].value_counts().head(8)
    if counts.empty:
        return None
    with plt.rc_context(PLT_STYLE):
        fig, ax = plt.subplots(figsize=(10, 4.5))
        bars = ax.barh(counts.index.astype(str), counts.values, color=PALETTE[:len(counts)], edgecolor="#0e1117")
        for bar, val in zip(bars, counts.values):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", ha="left", color="#c9d1d9", fontsize=10)
        ax.set_xlabel("Count")
        ax.set_title("Property Type Breakdown", fontsize=14, fontweight="bold", color="white")
        ax.invert_yaxis()
        ax.grid(axis="x")
    return _save_fig(fig, "type_breakdown")


def _chart_discount_scatter(df: pd.DataFrame) -> Path | None:
    sub = df.dropna(subset=["discount_pct", "price"])
    sub = sub[sub["discount_pct"] > 0]
    if sub.empty:
        return None
    with plt.rc_context(PLT_STYLE):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(sub["price"], sub["discount_pct"], c=RED, s=50, alpha=0.75, edgecolors="#30363d", linewidths=0.4)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(_fmt_price))
        ax.set_xlabel("Price")
        ax.set_ylabel("Discount %")
        ax.set_title("Price Reductions — Who Is Dropping?", fontsize=14, fontweight="bold", color="white")
        ax.grid(True, alpha=0.3)
    return _save_fig(fig, "discount_scatter")


# ─── HTML BUILDER ─────────────────────────────────────────────


def _summary_stats(df: pd.DataFrame) -> dict:
    stats = {"total": len(df)}
    if "price" in df.columns:
        p = df["price"].dropna()
        stats["avg_price"] = p.mean()
        stats["med_price"] = p.median()
        stats["min_price"] = p.min()
        stats["max_price"] = p.max()
    if "days_on_market" in df.columns:
        stats["avg_dom"] = df["days_on_market"].dropna().mean()
    if "sqft" in df.columns:
        stats["avg_sqft"] = df["sqft"].dropna().mean()
    if "price_per_sqft" in df.columns:
        stats["med_ppsf"] = df["price_per_sqft"].dropna().median()
    return stats


def _top_deals_table(df: pd.DataFrame, n: int = 5) -> str:
    cols_want = ["address", "price", "sqft", "beds", "baths", "days_on_market", "price_per_sqft", "discount_pct"]
    cols_have = [c for c in cols_want if c in df.columns]
    if not cols_have:
        return ""

    if "price_per_sqft" in df.columns:
        top = df.dropna(subset=["price_per_sqft"]).nsmallest(n, "price_per_sqft")
    elif "price" in df.columns:
        top = df.dropna(subset=["price"]).nsmallest(n, "price")
    else:
        return ""

    rows_html = ""
    for _, r in top.iterrows():
        cells = ""
        for c in cols_have:
            val = r.get(c)
            if pd.isna(val):
                cells += "<td>—</td>"
            elif c == "price":
                cells += f"<td>{_fmt_price(val)}</td>"
            elif c == "price_per_sqft":
                cells += f"<td>${val:,.0f}</td>"
            elif c == "discount_pct":
                cells += f"<td>{val:.1f}%</td>"
            elif c in ("sqft", "beds", "baths", "days_on_market"):
                cells += f"<td>{int(val) if val == int(val) else val}</td>"
            else:
                cells += f"<td>{val}</td>"
        rows_html += f"<tr>{cells}</tr>\n"

    header_map = {
        "address": "Address", "price": "Price", "sqft": "Sqft",
        "beds": "Beds", "baths": "Baths", "days_on_market": "DOM",
        "price_per_sqft": "$/sqft", "discount_pct": "Discount %",
    }
    headers = "".join(f"<th>{header_map.get(c, c)}</th>" for c in cols_have)
    return f"""
    <table>
      <thead><tr>{headers}</tr></thead>
      <tbody>{rows_html}</tbody>
    </table>"""


def _build_html(stats: dict, charts: list[Path], deals_table: str) -> str:
    def _kpi(label, value):
        return f'<div class="kpi"><div class="kpi-val">{value}</div><div class="kpi-label">{label}</div></div>'

    kpis = _kpi("Properties", f"{stats['total']}")
    if "avg_price" in stats:
        kpis += _kpi("Avg Price", _fmt_price(stats["avg_price"]))
        kpis += _kpi("Median Price", _fmt_price(stats["med_price"]))
    if "med_ppsf" in stats:
        kpis += _kpi("Median $/sqft", f"${stats['med_ppsf']:,.0f}")
    if "avg_dom" in stats:
        kpis += _kpi("Avg Days on Market", f"{stats['avg_dom']:.0f}")
    if "avg_sqft" in stats:
        kpis += _kpi("Avg Sqft", f"{stats['avg_sqft']:,.0f}")

    chart_html = ""
    for p in charts:
        chart_html += f'<div class="chart-card"><img src="{p}" /></div>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Detroit Real Estate Insights</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:#0e1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;padding:32px 48px}}
  h1{{font-size:28px;color:#fff;margin-bottom:4px}}
  .subtitle{{color:#8b949e;font-size:14px;margin-bottom:28px}}
  .kpi-row{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:32px}}
  .kpi{{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:20px 24px;min-width:150px;flex:1;text-align:center}}
  .kpi-val{{font-size:26px;font-weight:700;color:#58a6ff}}
  .kpi-label{{font-size:12px;color:#8b949e;margin-top:4px;text-transform:uppercase;letter-spacing:.5px}}
  h2{{font-size:20px;color:#fff;margin:32px 0 12px;border-bottom:1px solid #21262d;padding-bottom:8px}}
  .chart-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:20px}}
  .chart-card{{background:#161b22;border:1px solid #30363d;border-radius:10px;overflow:hidden;padding:8px}}
  .chart-card img{{width:100%;display:block;border-radius:6px}}
  table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:13px}}
  th{{background:#161b22;color:#58a6ff;text-align:left;padding:10px 12px;border-bottom:2px solid #30363d}}
  td{{padding:8px 12px;border-bottom:1px solid #21262d}}
  tr:hover td{{background:#1c2128}}
</style>
</head>
<body>
  <h1>Detroit Real Estate — Market Insights</h1>
  <div class="subtitle">Auto-generated EDA report &middot; {pd.Timestamp.now().strftime('%B %d, %Y')}</div>

  <div class="kpi-row">{kpis}</div>

  <h2>Top Value Picks (lowest $/sqft)</h2>
  {deals_table}

  <h2>Charts</h2>
  <div class="chart-grid">
    {chart_html}
  </div>
</body>
</html>"""


# ─── PUBLIC FUNCTION ──────────────────────────────────────────


def _eda_1304_i1_GET_report(df: pd.DataFrame) -> pd.DataFrame:
    out = _prep(df)

    charts: list[Path] = []
    for builder in (
        _chart_price_distribution,
        _chart_price_per_sqft,
        _chart_price_vs_sqft,
        _chart_beds_price_box,
        _chart_dom_distribution,
        _chart_type_breakdown,
        _chart_discount_scatter,
    ):
        path = builder(out)
        if path is not None:
            charts.append(path)

    stats = _summary_stats(out)
    deals_table = _top_deals_table(out)
    html = _build_html(stats, charts, deals_table)

    Path(HTML_OUT).write_text(html, encoding="utf-8")
    return out
