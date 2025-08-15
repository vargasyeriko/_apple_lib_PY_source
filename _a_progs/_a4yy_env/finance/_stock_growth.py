# -----######-----###### TERMINAL STOCK GROWTH DASH — CORE FN (TQM, Sparklines, Rank Bars) -----######-----###### #
# deps: pip install rich pandas
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.rule import Rule
from rich import box
import math

try:
    import pandas as pd
except Exception:
    pd = None

console = Console()

# -- sub: quick sparkline from a numeric series (length-agnostic)
def _sparkline_levels_(_series):
    # unicode blocks from low->high
    blocks = "▁▂▃▄▅▆▇█"
    if not _series:
        return ""
    lo, hi = min(_series), max(_series)
    rng = hi - lo if hi != lo else 1e-9
    out = []
    for v in _series:
        idx = int((v - lo) / rng * (len(blocks) - 1))
        out.append(blocks[idx])
    return "".join(out)

# -- sub: draw a colored rank bar relative to peers
def _rank_bar_(val, max_abs, width=28):
    width = max(10, width)
    if max_abs <= 0:
        return ""
    frac = min(1.0, abs(val) / max_abs)
    length = max(0, int(frac * width))
    bar = "█" * length
    color = "green" if val >= 0 else "red"
    return f"[{color}]{bar}[/{color}] {val:+.2f}%"

# -----######-----###### MAIN IMPORTABLE FN -----######-----###### #
def _stock_0814_i1_GET_term_growthdash(
    prices_dict=None,         # dict: {"AAPL":[p1,p2,...], "MSFT":[...], ...}
    df=None,                  # optional pandas DataFrame (wide): index=date-like, columns=tickers
    tickers=None,             # list of columns to use if df provided; default = all numeric cols
    title="Stock Growth — Terminal Dashboard",
    baseline="first",         # "first" or a YYYY-MM-DD string present in df.index
    width_rank_bar=28,
    show_per_stock_drawdown=True,
    sort_by="return",         # "return" | "drawdown" | "cagr"
    assume_periods_per_year=252  # used if index is not datetime (fallback annualization)
):
    """
    Returns a pandas DataFrame with metrics and prints a terminal dashboard.
    Accepted inputs:
      - prices_dict: {"TICK": [p1, p2, ...]}
      - df (wide): index=Date (prefer datetime), columns=tickers; pass 'tickers' to choose subset
    """
    # ---- Resolve series ----
    if df is not None:
        if pd is None:
            raise RuntimeError("pandas not available; install pandas or use prices_dict.")
        _df = df.copy()
        # try to coerce index to datetime if possible
        try:
            _df.index = pd.to_datetime(_df.index)
            index_is_datetime = True
        except Exception:
            index_is_datetime = False
        if tickers is None:
            # keep numeric columns
            tickers = [c for c in _df.columns if pd.api.types.is_numeric_dtype(_df[c])]
        _df = _df[tickers].dropna(how="all")
        # choose baseline row
        if baseline == "first":
            base_row = _df.iloc[0]
        else:
            # user supplied date string
            if index_is_datetime:
                # pick the closest on/after date
                try:
                    baseline_ts = pd.to_datetime(baseline)
                    base_row = _df.loc[_df.index.get_indexer([baseline_ts], method="nearest")]
                    base_row = _df.iloc[ base_row[0] ]
                except Exception:
                    # fallback to first
                    base_row = _df.iloc[0]
            else:
                base_row = _df.iloc[0]
        # build dict of series (drop NaNs per ticker)
        prices_dict = {}
        for t in tickers:
            s = _df[t].dropna().astype(float).tolist()
            if len(s) >= 2:
                prices_dict[t] = s
        # horizon for cagr
        if index_is_datetime and len(_df.index) >= 2:
            days = (_df.index[-1] - _df.index[0]).days
            periods_per_year = 365.25 / max(1, days) * (len(_df.index) - 1)
        else:
            periods_per_year = assume_periods_per_year
    else:
        if not prices_dict:
            raise ValueError("Provide prices_dict or df.")
        periods_per_year = assume_periods_per_year

    tickers = list(prices_dict.keys())
    if not tickers:
        raise ValueError("No valid series to display.")

    # ---- TQM progress ----
    with Progress(
        TextColumn("[bold]TQM[/bold] • Processing:", justify="right"),
        BarColumn(bar_width=None),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("metrics", total=len(tickers) + 3)

        rows = []
        for t in tickers:
            series = [float(x) for x in prices_dict[t] if x is not None]
            if len(series) < 2:
                progress.advance(task); continue

            start = series[0]
            end = series[-1]
            ret = (end / start - 1.0) * 100.0

            # drawdown
            peak = series[0]
            max_dd = 0.0
            for p in series:
                peak = max(peak, p)
                dd = (p / peak - 1.0) * 100.0
                if dd < max_dd:
                    max_dd = dd

            # CAGR (approx; assumes regular spacing)
            try:
                years = max(1e-9, (len(series) - 1) / periods_per_year)
                cagr = (end / start) ** (1.0 / years) - 1.0
            except Exception:
                cagr = float("nan")

            # normalized index for sparkline (100 at start)
            norm = [(p / start) * 100.0 for p in series]
            spark = _sparkline_levels_(norm)

            rows.append({
                "ticker": t,
                "start": start,
                "end": end,
                "return_pct": ret,
                "max_drawdown_pct": max_dd,
                "cagr_pct": cagr * 100.0 if not math.isnan(cagr) else float("nan"),
                "spark": spark,
                "norm_last": norm[-1]
            })
            progress.advance(task)

        progress.advance(task); progress.advance(task); progress.advance(task)

    # ---- sort
    if sort_by == "drawdown":
        rows.sort(key=lambda r: r["max_drawdown_pct"])  # most negative first
    elif sort_by == "cagr":
        rows.sort(key=lambda r: (float("-inf") if math.isnan(r["cagr_pct"]) else r["cagr_pct"]), reverse=True)
    else:
        rows.sort(key=lambda r: r["return_pct"], reverse=True)

    # ---- Header
    header = Panel.fit(
        f"[bold white]{title}[/bold white]\n"
        f"[dim]Normalized growth (sparkline), total return ranking, and max drawdown[/dim]",
        border_style="cyan", padding=(1, 2)
    )
    console.print(header)

    # ---- KPI table (aggregate)
    if rows:
        best = rows[0]
        worst = rows[-1]
        kpi_tbl = Table.grid(padding=(0, 3))
        kpi_tbl.add_column(justify="right", style="bold")
        kpi_tbl.add_column(justify="left")
        kpi_tbl.add_row("Leaders (Return)", f"[green]{best['ticker']} {best['return_pct']:+.2f}%[/green]")
        kpi_tbl.add_row("Laggards (Return)", f"[red]{worst['ticker']} {worst['return_pct']:+.2f}%[/red]")
        kpi_tbl.add_row("Count", f"{len(rows)} tickers")
        console.print(Panel(kpi_tbl, title="Overview", title_align="left", border_style="magenta", padding=(1,2)))

    console.print(Rule(style="dim"))

    # ---- Detail table
    max_abs_ret = max(abs(r["return_pct"]) for r in rows) if rows else 1.0

    tbl = Table(box=box.SIMPLE_HEAVY)
    tbl.add_column("Ticker", style="cyan", no_wrap=True)
    tbl.add_column("Spark (norm idx)", justify="left")
    tbl.add_column("Rank Bar (vs peers)", justify="left")
    tbl.add_column("Return", justify="right")
    if show_per_stock_drawdown:
        tbl.add_column("Max DD", justify="right")
    tbl.add_column("CAGR*", justify="right")
    tbl.add_column("Start→End", justify="right")

    for r in rows:
        rank_bar = _rank_bar_(r["return_pct"], max_abs_ret, width=width_rank_bar)
        ret_txt = f"{r['return_pct']:+.2f}%"
        dd_txt = f"{r['max_drawdown_pct']:.2f}%"
        cagr_txt = "-" if math.isnan(r["cagr_pct"]) else f"{r['cagr_pct']:.2f}%"
        start_end = f"{r['start']:,.2f} → {r['end']:,.2f}"
        row_vals = [
            f"[bold]{r['ticker']}[/bold]",
            r["spark"],
            rank_bar,
            ret_txt
        ]
        if show_per_stock_drawdown:
            row_vals.append(dd_txt)
        row_vals.extend([cagr_txt, start_end])
        tbl.add_row(*row_vals)

    console.print(tbl)
    console.print(Panel.fit("[dim]* CAGR assumes evenly spaced observations[/dim]", border_style="yellow"))

    # ---- return metrics as DataFrame
    if pd is not None:
        return pd.DataFrame(rows)[["ticker","start","end","return_pct","max_drawdown_pct","cagr_pct","spark","norm_last"]]
    else:
        return rows

# -----######-----###### END CORE FN -----######-----###### #
# Example call — replace with *your* data (df or dict). No sample DataFrames created here.

# 1) If you already have a wide DataFrame `df_prices` with date index and columns = tickers:
# out = _stock_0814_i1_GET_term_growthdash(
#     df=df_prices,
#     tickers=["AAPL","MSFT","NVDA","TSLA"],   # or None to auto-pick numeric cols
#     title="Weekly Watch — Normalized Growth & Ranking",
#     baseline="first",                        # or "2025-08-08" etc if in index
#     sort_by="return"                         # "return" | "drawdown" | "cagr"
# )

# 2) Or pass a simple dict of lists (all same length):
prices = {
  "AAPL": [211, 212, 214, 218, 217],
  "MSFT": [425, 427, 429, 431, 435],
  "TSLA": [245, 250, 248, 255, 260]
}
out = _stock_0814_i1_GET_term_growthdash(
    prices_dict=prices,
    title="Friday Check — Terminal Growth Dash",
    sort_by="return"
)

print(out)  # DataFrame or list of dicts with metrics (ticker, return_pct, max_drawdown_pct, cagr_pct, spark)
