"""
function_fin.py — 10 Terminal-Based Financial Analysis Functions
================================================================
Each function takes a DataFrame of OHLCV data (from yfinance) and a ticker string,
then prints a styled ASCII visualization directly to the terminal.

Every function is wrapped with try/except so one crash never kills the app.
"""

import numpy as np
import pandas as pd


# ######################################################################
#  INTERNAL HELPER — safely flatten any yfinance DataFrame
# ######################################################################

def _safe_col(df, col):
    """Extract a column as a flat 1-D numpy array, no matter the DF shape."""
    if col not in df.columns:
        for c in df.columns:
            cstr = str(c).lower()
            if col.lower() in cstr:
                s = df[c].dropna()
                return s.values.flatten() if hasattr(s.values, "flatten") else np.array(s.values)
        return np.array([])
    s = df[col].dropna()
    return s.values.flatten() if hasattr(s.values, "flatten") else np.array(s.values)


def _safe_series(df, col):
    """Extract a column as a pandas Series, no matter the DF shape."""
    if col not in df.columns:
        for c in df.columns:
            if col.lower() in str(c).lower():
                return df[c].dropna().squeeze()
        return pd.Series(dtype=float)
    return df[col].dropna().squeeze()


# ######################################################################
# ######################################################################
# ##                                                                  ##
# ##   1. VOLATILITY + TREND COMPRESSION                              ##
# ##                                                                  ##
# ######################################################################
# ######################################################################

def volatility_trend(df, ticker, window=30):
    """
    Sparkline of price path + volatility intensity markers.
    Smooth blocks + low dots = clean trend.
    Jagged + !!! = danger / chop.
    """
    try:
        close = _safe_col(df, "Close")
        if len(close) < 5:
            print(f"  {ticker} — TREND / VOL: not enough data"); return

        returns = np.diff(close) / close[:-1]

        blocks = "▁▂▃▄▅▆▇█"
        mn, mx = float(close.min()), float(close.max())
        rng = mx - mn if mx != mn else 1.0
        n_points = min(40, len(close))
        indices = np.linspace(0, len(close) - 1, n_points, dtype=int)
        sampled = close[indices]
        sparkline = ""
        for v in sampled:
            idx = int(float(v - mn) / rng * (len(blocks) - 1))
            idx = max(0, min(idx, len(blocks) - 1))
            sparkline += blocks[idx]

        roll_vol = pd.Series(returns).rolling(min(window, len(returns))).std().dropna().values
        if len(roll_vol) == 0:
            vol_line = ".  " * n_points
        else:
            vol_idx = np.linspace(0, len(roll_vol) - 1, n_points, dtype=int)
            vol_sampled = roll_vol[vol_idx]
            vmin, vmax = float(vol_sampled.min()), float(vol_sampled.max())
            vrng = vmax - vmin if vmax != vmin else 1.0
            vol_line = ""
            for v in vol_sampled:
                norm = float(v - vmin) / vrng
                if norm < 0.33:
                    vol_line += ".  "
                elif norm < 0.66:
                    vol_line += ":  "
                else:
                    vol_line += "!  "

        w = min(window, len(returns))
        annual_vol = float(np.std(returns[-w:])) * np.sqrt(252) * 100 if w > 0 else 0

        print()
        print(f"  {ticker} — TREND / VOL ({window}D)")
        print(f"  {'─' * 44}")
        print(f"  Price Path:")
        print(f"  {sparkline}")
        print()
        print(f"  Volatility:")
        print(f"  {vol_line.rstrip()}")
        print(f"  {'─' * 44}")
        print(f"  Legend:  ▁▇ = price progression")
        print(f"           . : ! = low → med → high volatility")
        print(f"  Annual Vol ({window}D): {annual_vol:.1f}%")
        print()
    except Exception as e:
        print(f"  {ticker} — TREND / VOL: ERROR → {e}")


# ######################################################################
# ######################################################################
# ##                                                                  ##
# ##   2. MOMENTUM DECAY RADAR                                        ##
# ##                                                                  ##
# ######################################################################
# ######################################################################

def momentum_decay(df, ticker, lookback=5):
    """
    Shows if a recent move is losing power.
    Even if price is up, shrinking bars = exit warning.
    """
    try:
        close = _safe_series(df, "Close")
        if len(close) < lookback + 1:
            print(f"  {ticker} — MOMENTUM DECAY: not enough data"); return

        returns = close.pct_change().dropna().tail(lookback)

        print()
        print(f"  {ticker} — MOMENTUM DECAY")
        print(f"  {'─' * 36}")
        print(f"  {'Day':<7} {'Return':>8}   Momentum")
        print(f"  {'─' * 36}")

        max_abs = float(returns.abs().max()) if float(returns.abs().max()) > 0 else 1.0
        for i, (date, ret) in enumerate(returns.items()):
            ret = float(ret)
            n_bars = int(abs(ret) / max_abs * 12)
            bar = "█" * max(n_bars, 1)
            sign = "+" if ret >= 0 else ""
            label = f"D-{lookback - i}"
            print(f"  {label:<7} {sign}{ret*100:>6.2f}%   {bar}")

        print(f"  {'─' * 36}")

        vals = returns.values.flatten().astype(float)
        if len(vals) >= 3:
            recent_avg = np.mean(np.abs(vals[-2:]))
            older_avg = np.mean(np.abs(vals[:-2]))
            if older_avg > 0 and recent_avg < older_avg * 0.6:
                signal = "MOMENTUM COLLAPSING"
            elif older_avg > 0 and recent_avg < older_avg * 0.85:
                signal = "MOMENTUM WEAKENING"
            elif older_avg > 0 and recent_avg > older_avg * 1.2:
                signal = "MOMENTUM ACCELERATING"
            else:
                signal = "MOMENTUM STEADY"
        else:
            signal = "INSUFFICIENT DATA"

        print(f"  Signal: {signal}")
        print()
    except Exception as e:
        print(f"  {ticker} — MOMENTUM DECAY: ERROR → {e}")


# ######################################################################
# ######################################################################
# ##                                                                  ##
# ##   3. SUPPORT / RESISTANCE HEATMAP                                ##
# ##                                                                  ##
# ######################################################################
# ######################################################################

def support_resistance(df, ticker, n_zones=8):
    """
    Volume-weighted price density heatmap.
    Thick zones = battle zones.  Thin zones = fast moves.
    """
    try:
        close = _safe_col(df, "Close")
        volume = _safe_col(df, "Volume")
        if len(close) < 5 or len(volume) < 5:
            print(f"  {ticker} — PRICE ZONES: not enough data"); return

        mn = min(len(close), len(volume))
        close = close[:mn]
        volume = volume[:mn]
        current = float(close[-1])

        lo, hi = float(close.min()), float(close.max())
        if lo == hi:
            hi = lo + 1
        edges = np.linspace(lo, hi, n_zones + 1)

        zone_vol = np.zeros(n_zones)
        for i in range(n_zones):
            mask = (close >= edges[i]) & (close < edges[i + 1])
            zone_vol[i] = float(volume[mask].sum())

        max_vol = float(zone_vol.max()) if zone_vol.max() > 0 else 1.0

        print()
        print(f"  {ticker} — PRICE ZONES (Volume Density)")
        print(f"  {'─' * 44}")

        for i in range(n_zones - 1, -1, -1):
            bar_len = int(zone_vol[i] / max_vol * 20)
            bar = "█" * max(bar_len, 0)
            lo_price = float(edges[i])
            hi_price = float(edges[i + 1])
            marker = ""
            if lo_price <= current <= hi_price:
                marker = " ← YOU ARE HERE"
            elif zone_vol[i] == zone_vol.max():
                marker = " ← heavy zone"
            print(f"  {hi_price:>7.0f} ┤ {bar}{marker}")

        print(f"  {'─' * 44}")
        print(f"  Density = historical traded volume per zone")
        print()
    except Exception as e:
        print(f"  {ticker} — PRICE ZONES: ERROR → {e}")


# ######################################################################
# ######################################################################
# ##                                                                  ##
# ##   4. REGIME DETECTOR                                             ##
# ##                                                                  ##
# ######################################################################
# ######################################################################

def regime_detector(df, ticker, window=30):
    """
    Detects the current market state by scoring trend, volatility, and liquidity.
    """
    try:
        close = _safe_series(df, "Close")
        volume = _safe_series(df, "Volume")
        if len(close) < window:
            print(f"  {ticker} — REGIME: not enough data"); return

        returns = close.pct_change().dropna()

        recent = close.tail(window).values.flatten().astype(float)
        x = np.arange(len(recent))
        slope = float(np.polyfit(x, recent, 1)[0]) if len(recent) > 1 else 0.0
        rmean = float(recent.mean()) if recent.mean() != 0 else 1.0
        trend_score = min(10, max(0, int(abs(slope) / (abs(rmean) * 0.001) * 2)))
        trend_dir = "BULL" if slope > 0 else "BEAR"

        vol = float(returns.tail(window).std()) * np.sqrt(252)
        vol_score = min(10, max(0, int(vol / 0.08)))

        vol_mean = float(volume.tail(window).mean())
        vol_std = float(volume.tail(window).std())
        vol_cv = vol_std / vol_mean if vol_mean > 0 else 1.0
        liq_score = min(10, max(0, int((1 - vol_cv) * 10)))

        def bar(score):
            filled = "█" * score
            empty = "░" * (10 - score)
            return f"{filled}{empty}  ({score}/10)"

        if trend_score >= 6 and vol_score <= 5:
            state = f"TRENDING {trend_dir}"
        elif trend_score >= 6 and vol_score > 5:
            state = f"VOLATILE {trend_dir}"
        elif trend_score < 4 and vol_score <= 4:
            state = "RANGE-BOUND"
        elif trend_score < 4 and vol_score > 4:
            state = "CHOPPY / UNCERTAIN"
        else:
            state = f"TRANSITIONING ({trend_dir})"

        print()
        print(f"  {ticker} — MARKET REGIME")
        print(f"  {'─' * 44}")
        print(f"  Trend Strength:  {bar(trend_score)}")
        print(f"  Volatility:      {bar(vol_score)}")
        print(f"  Liquidity:       {bar(liq_score)}")
        print()
        print(f"  STATE: {state}")
        print(f"  {'─' * 44}")
        print()
    except Exception as e:
        print(f"  {ticker} — REGIME: ERROR → {e}")


# ######################################################################
# ######################################################################
# ##                                                                  ##
# ##   5. BREAKOUT PRESSURE GAUGE                                     ##
# ##                                                                  ##
# ######################################################################
# ######################################################################

def breakout_pressure(df, ticker, window=20):
    """
    Measures how close price is to breaking resistance,
    combining structure + volume + price compression.
    """
    try:
        close = _safe_col(df, "Close")
        volume = _safe_col(df, "Volume")
        high = _safe_col(df, "High")
        if len(close) < window or len(high) < window:
            print(f"  {ticker} — BREAKOUT: not enough data"); return

        current = float(close[-1])
        resistance = float(np.max(high[-window:]))

        recent_low = float(np.min(close[-window:]))
        rng = resistance - recent_low
        if rng == 0:
            rng = 1.0
        pressure = int(((current - recent_low) / rng) * 100)
        pressure = min(100, max(0, pressure))

        vol_avg = float(np.mean(volume[-window:]))
        vol_recent = float(np.mean(volume[-5:])) if len(volume) >= 5 else vol_avg
        vol_spike = vol_recent > vol_avg * 1.3

        # Higher lows: split last `window` closes into 4 chunks, check if each chunk's min rises
        chunk_size = max(1, window // 4)
        tail = close[-window:]
        chunks = [tail[i:i+chunk_size] for i in range(0, len(tail), chunk_size) if len(tail[i:i+chunk_size]) > 0]
        chunk_mins = [float(np.min(c)) for c in chunks]
        higher_lows = all(chunk_mins[i] <= chunk_mins[i+1] for i in range(len(chunk_mins)-1)) if len(chunk_mins) >= 2 else False

        filled = int(pressure / 100 * 20)
        gauge = "█" * filled + "░" * (20 - filled)

        if pressure >= 85 and vol_spike and higher_lows:
            signal = "IMMINENT BREAKOUT"
        elif pressure >= 70:
            signal = "BUILDING PRESSURE"
        elif pressure >= 50:
            signal = "NEUTRAL"
        else:
            signal = "NO BREAKOUT SETUP"

        print()
        print(f"  {ticker} — BREAKOUT PRESSURE")
        print(f"  {'─' * 40}")
        print(f"  Resistance:   ${resistance:,.2f}")
        print(f"  Current:      ${current:,.2f}")
        print()
        print(f"  Pressure:")
        print(f"  [{gauge}] {pressure}%")
        print()
        print(f"  Volume Spike:  {'YES' if vol_spike else 'NO'}")
        print(f"  Higher Lows:   {'YES' if higher_lows else 'NO'}")
        print()
        print(f"  Signal: {signal}")
        print(f"  {'─' * 40}")
        print()
    except Exception as e:
        print(f"  {ticker} — BREAKOUT: ERROR → {e}")


# ######################################################################
# ######################################################################
# ##                                                                  ##
# ##   6. RISK MAP                                                    ##
# ##                                                                  ##
# ######################################################################
# ######################################################################

def risk_map(df, ticker, n_zones=5):
    """
    Risk/reward zones based on where price sits relative to support/resistance.
    """
    try:
        close = _safe_col(df, "Close")
        if len(close) < 5:
            print(f"  {ticker} — RISK MAP: not enough data"); return

        current = float(close[-1])
        lo, hi = float(close.min()), float(close.max())
        rng = hi - lo if hi != lo else 1.0

        edges = np.linspace(lo - rng * 0.05, hi + rng * 0.05, n_zones + 1)

        print()
        print(f"  {ticker} — RISK MAP")
        print(f"  {'─' * 48}")
        print(f"  {'Zone':<18} {'Risk':<10} {'Reward':<10}")
        print(f"  {'─' * 48}")

        for i in range(n_zones - 1, -1, -1):
            zone_lo = float(edges[i])
            zone_hi = float(edges[i + 1])
            mid = (zone_lo + zone_hi) / 2.0

            dist_from_current = (mid - current) / current * 100 if current != 0 else 0

            if dist_from_current > 8:
                risk, reward = "HIGH", "LOW"
            elif dist_from_current > 3:
                risk, reward = "MED", "MED"
            elif dist_from_current > -3:
                risk, reward = "MED", "MED"
            elif dist_from_current > -8:
                risk, reward = "LOW", "HIGH"
            else:
                risk, reward = "MED", "HIGH"

            marker = ""
            if zone_lo <= current <= zone_hi:
                marker = " ← CURRENT"
            elif risk == "LOW" and reward == "HIGH":
                marker = " ← IDEAL"

            label = f"${zone_lo:>7,.0f}–{zone_hi:>7,.0f}"
            print(f"  {label:<18} {risk:<10} {reward:<10}{marker}")

        print(f"  {'─' * 48}")
        print()
    except Exception as e:
        print(f"  {ticker} — RISK MAP: ERROR → {e}")


# ######################################################################
# ######################################################################
# ##                                                                  ##
# ##   7. CORRELATION CLUSTER VIEW                                    ##
# ##                                                                  ##
# ######################################################################
# ######################################################################

def correlation_cluster(df_dict, ticker, peers):
    """
    Shows pairwise correlation between a ticker and its peers.
    df_dict: dict of {ticker: DataFrame} for all tickers.
    peers: list of peer ticker strings.
    """
    try:
        all_tickers = [ticker] + peers
        returns = pd.DataFrame()
        for t in all_tickers:
            if t in df_dict:
                r = _safe_series(df_dict[t], "Close").pct_change().dropna()
                returns[t] = r

        if returns.empty or len(returns.columns) < 2:
            print(f"  {ticker} — CORRELATION: not enough peer data"); return

        corr = returns.corr()

        print()
        print(f"  {ticker} — CORRELATION CLUSTER")
        print(f"  {'─' * 44}")

        center = ticker
        lines_out = []
        for p in peers:
            if p in corr.columns and center in corr.index:
                c = float(corr.loc[center, p])
                lines_out.append((p, c))

        if len(lines_out) >= 4:
            p1, _ = lines_out[0]
            p2, _ = lines_out[1]
            p3, _ = lines_out[2]
            p4, _ = lines_out[3] if len(lines_out) >= 4 else lines_out[2]
            print(f"         {center} ───── {p1}")
            print(f"           │         │")
            print(f"           │         │")
            print(f"         {p3} ───── {p2}")
        elif len(lines_out) >= 2:
            p1, _ = lines_out[0]
            p2, _ = lines_out[1]
            print(f"         {center} ───── {p1}")
            print(f"           │")
            print(f"         {p2}")
        elif len(lines_out) == 1:
            p1, _ = lines_out[0]
            print(f"         {center} ───── {p1}")

        print(f"  {'─' * 44}")
        print(f"  Correlations:")
        for p, c in lines_out:
            strength = "VERY HIGH" if c > 0.85 else "HIGH" if c > 0.7 else "MODERATE" if c > 0.5 else "LOW"
            print(f"    {center}–{p:<6}  {c:.2f}  ({strength})")

        all_corrs = [c for _, c in lines_out]
        if all_corrs and np.mean(all_corrs) > 0.8:
            print()
            print(f"  WARNING: Not diversified → leveraged on same bet")
        print()
    except Exception as e:
        print(f"  {ticker} — CORRELATION: ERROR → {e}")


# ######################################################################
# ######################################################################
# ##                                                                  ##
# ##   8. MEAN REVERSION SIGNAL                                       ##
# ##                                                                  ##
# ######################################################################
# ######################################################################

def mean_reversion(df, ticker, window=20):
    """
    How far price is from its rolling mean.
    Stretched = snapback probability.
    """
    try:
        close = _safe_series(df, "Close")
        if len(close) < window:
            print(f"  {ticker} — MEAN REVERSION: not enough data"); return

        mean_val = float(close.rolling(window).mean().iloc[-1])
        current = float(close.iloc[-1])

        if mean_val > 0:
            distance_pct = (current - mean_val) / mean_val * 100
        else:
            distance_pct = 0.0

        abs_dist = abs(distance_pct)
        filled = min(20, int(abs_dist / 15 * 20))
        gauge = "█" * filled + "░" * (20 - filled)

        if abs_dist > 10:
            signal = "VERY STRETCHED"
        elif abs_dist > 5:
            signal = "STRETCHED"
        elif abs_dist > 2:
            signal = "SLIGHTLY EXTENDED"
        else:
            signal = "NEAR MEAN (NEUTRAL)"

        direction = "ABOVE" if distance_pct > 0 else "BELOW"

        print()
        print(f"  {ticker} — MEAN DISTANCE ({window}D)")
        print(f"  {'─' * 36}")
        print(f"  Mean ({window}D):  ${mean_val:>10,.2f}")
        print(f"  Current:    ${current:>10,.2f}")
        print()
        print(f"  Distance:   {'+' if distance_pct > 0 else ''}{distance_pct:.1f}%  ({direction})")
        print()
        print(f"  {gauge}")
        print()
        print(f"  Signal: {signal}")
        print(f"  {'─' * 36}")
        print()
    except Exception as e:
        print(f"  {ticker} — MEAN REVERSION: ERROR → {e}")


# ######################################################################
# ######################################################################
# ##                                                                  ##
# ##   9. SMART MONEY TRACKER (VOLUME INTENT)                         ##
# ##                                                                  ##
# ######################################################################
# ######################################################################

def smart_money(df, ticker, window=30):
    """
    Compares volume on up-days vs down-days.
    Accumulation = buyers in control.  Distribution = sellers.
    """
    try:
        recent = df.tail(window).copy()
        close = _safe_series(recent, "Close")
        volume = _safe_series(recent, "Volume")
        if len(close) < 5 or len(volume) < 5:
            print(f"  {ticker} — VOLUME INTENT: not enough data"); return

        returns = close.pct_change()

        up_vol = float(volume[returns > 0].sum())
        down_vol = float(volume[returns <= 0].sum())
        total = up_vol + down_vol if (up_vol + down_vol) > 0 else 1.0

        up_pct = up_vol / total * 100
        down_pct = down_vol / total * 100

        up_bar_len = int(up_pct / 100 * 20)
        down_bar_len = int(down_pct / 100 * 20)

        if up_pct > 65:
            bias = "STRONG ACCUMULATION"
        elif up_pct > 55:
            bias = "ACCUMULATION"
        elif down_pct > 65:
            bias = "STRONG DISTRIBUTION"
        elif down_pct > 55:
            bias = "DISTRIBUTION"
        else:
            bias = "NEUTRAL / BALANCED"

        print()
        print(f"  {ticker} — VOLUME INTENT ({window}D)")
        print(f"  {'─' * 44}")
        print(f"  Up Days Volume:    {'█' * up_bar_len}{'░' * (20 - up_bar_len)}  {up_pct:.0f}%")
        print(f"  Down Days Volume:  {'█' * down_bar_len}{'░' * (20 - down_bar_len)}  {down_pct:.0f}%")
        print()
        print(f"  Bias: {bias}")
        print(f"  {'─' * 44}")
        print()
    except Exception as e:
        print(f"  {ticker} — VOLUME INTENT: ERROR → {e}")


# ######################################################################
# ######################################################################
# ##                                                                  ##
# ##   10. DECISION ENGINE (FINAL OUTPUT)                             ##
# ##                                                                  ##
# ######################################################################
# ######################################################################

def decision_engine(df, ticker, window=30):
    """
    Aggregates all signals into a single trade decision with confidence score.
    """
    try:
        close = _safe_series(df, "Close")
        if len(close) < window:
            print(f"  {ticker} — DECISION: not enough data"); return

        returns = close.pct_change().dropna()
        current = float(close.iloc[-1])

        # --- Trend ---
        recent = close.tail(window).values.flatten().astype(float)
        x = np.arange(len(recent))
        slope = float(np.polyfit(x, recent, 1)[0]) if len(recent) > 1 else 0.0
        rmean = float(recent.mean()) if recent.mean() != 0 else 1.0
        trend_pct = slope / abs(rmean) * 100 * window
        if trend_pct > 5:
            trend_label, trend_score = "STRONG UP", 9
        elif trend_pct > 2:
            trend_label, trend_score = "UP", 7
        elif trend_pct > -2:
            trend_label, trend_score = "FLAT", 5
        elif trend_pct > -5:
            trend_label, trend_score = "DOWN", 3
        else:
            trend_label, trend_score = "STRONG DOWN", 1

        # --- Momentum ---
        last_5 = returns.tail(5).values.flatten().astype(float)
        if len(last_5) >= 4:
            recent_mag = float(np.mean(np.abs(last_5[-2:])))
            older_mag = float(np.mean(np.abs(last_5[:3])))
            ratio = recent_mag / older_mag if older_mag > 0 else 1.0
            if ratio > 1.2:
                mom_label, mom_score = "ACCELERATING", 8
            elif ratio > 0.8:
                mom_label, mom_score = "STEADY", 6
            elif ratio > 0.5:
                mom_label, mom_score = "WEAKENING", 4
            else:
                mom_label, mom_score = "COLLAPSING", 2
        else:
            mom_label, mom_score = "N/A", 5

        # --- Volatility ---
        vol = float(returns.tail(window).std()) * np.sqrt(252)
        if vol < 0.2:
            vol_label, vol_score = "LOW", 8
        elif vol < 0.4:
            vol_label, vol_score = "MEDIUM", 6
        elif vol < 0.6:
            vol_label, vol_score = "HIGH", 3
        else:
            vol_label, vol_score = "EXTREME", 1

        # --- Position (distance from mean) ---
        mean_val = float(close.rolling(window).mean().iloc[-1])
        dist = (current - mean_val) / mean_val * 100 if mean_val > 0 else 0.0
        if abs(dist) > 8:
            pos_label, pos_score = "EXTENDED", 3
        elif abs(dist) > 4:
            pos_label, pos_score = "STRETCHED", 5
        else:
            pos_label, pos_score = "FAIR VALUE", 8

        # --- Entry zone ---
        tail_vals = close.tail(window).values.flatten().astype(float)
        support = float(np.min(tail_vals))
        entry_lo = support
        entry_hi = mean_val

        # --- Confidence ---
        confidence = (trend_score + mom_score + vol_score + pos_score) / 4.0

        # --- Action ---
        if trend_score >= 7 and pos_label == "FAIR VALUE" and mom_score >= 6:
            action = ["BUY / ADD TO POSITION", "Trend is strong and price is fair"]
        elif trend_score >= 7 and pos_label in ("EXTENDED", "STRETCHED"):
            action = ["WAIT FOR PULLBACK", "DO NOT CHASE — price is extended"]
        elif trend_score <= 3 and pos_label == "FAIR VALUE":
            action = ["REDUCE EXPOSURE", "Trend is weak, protect capital"]
        elif trend_score <= 3 and pos_label in ("EXTENDED", "STRETCHED"):
            action = ["SELL / EXIT", "Weak trend + overextended = danger"]
        else:
            action = ["HOLD / MONITOR", "No clear edge — wait for signal"]

        print()
        print(f"  {ticker} — TRADE DECISION")
        print(f"  {'═' * 44}")
        print(f"  Trend:        {trend_label}")
        print(f"  Momentum:     {mom_label}")
        print(f"  Volatility:   {vol_label}")
        print(f"  Position:     {pos_label}")
        print()
        print(f"  Entry Zone:   ${entry_lo:,.2f} – ${entry_hi:,.2f}")
        print(f"  Current:      ${current:,.2f}")
        print()
        print(f"  ACTION:")
        for line in action:
            print(f"  → {line}")
        print(f"  {'═' * 44}")
        print(f"  Confidence: {confidence:.1f} / 10")
        print(f"  {'═' * 44}")
        print()
    except Exception as e:
        print(f"  {ticker} — DECISION: ERROR → {e}")
