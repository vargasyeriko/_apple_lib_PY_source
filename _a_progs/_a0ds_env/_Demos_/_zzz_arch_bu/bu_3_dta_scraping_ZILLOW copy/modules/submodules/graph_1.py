from __future__ import annotations

import math
import pickle
from pathlib import Path

import folium
import numpy as np
import pandas as pd
from folium.plugins import HeatMap, MarkerCluster
from geopy import exc as geopy_exc
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from tqdm.auto import tqdm


GEOPY_EXCEPTIONS = tuple(
    exc
    for exc in (
        getattr(geopy_exc, "GeocoderTimedOut", None),
        getattr(geopy_exc, "GeocoderUnavailable", None),
        getattr(geopy_exc, "GeocoderServiceError", None),
    )
    if exc is not None
)


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _normalize(series: pd.Series) -> pd.Series:
    valid = series.dropna()
    if valid.empty:
        return pd.Series(np.nan, index=series.index)
    min_val = valid.min()
    max_val = valid.max()
    denom = max(max_val - min_val, 1e-12)
    return (series - min_val) / denom


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _blend(c1: str, c2: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    rgb = (
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t),
    )
    return _rgb_to_hex(rgb)


def _value_to_cheap_expensive_color(value_01: float) -> str:
    green = "#2ecc71"
    yellow = "#f1c40f"
    red = "#e74c3c"
    if math.isnan(value_01):
        return "#3498db"
    if value_01 <= 0.5:
        return _blend(green, yellow, value_01 / 0.5)
    return _blend(yellow, red, (value_01 - 0.5) / 0.5)


def _value_to_deal_color(value_01: float) -> str:
    if math.isnan(value_01):
        return "#3498db"
    return _blend("#e74c3c", "#2ecc71", value_01)


def _value_to_days_on_market_color(value_01: float) -> str:
    # 0 = newest (red) → 0.5 = mid (yellow) → 1 = oldest/sitting (green)
    red = "#e74c3c"
    yellow = "#f1c40f"
    green = "#2ecc71"
    if math.isnan(value_01):
        return "#3498db"
    if value_01 <= 0.5:
        return _blend(red, yellow, value_01 / 0.5)
    return _blend(yellow, green, (value_01 - 0.5) / 0.5)


def _popup_html(row: pd.Series, marker_label: str | None = None) -> str:
    lines = [f"<b>Address:</b> {row.get('address', '')}"]
    if marker_label:
        lines.insert(0, f"<b>{marker_label}</b>")
    if "price" in row.index and pd.notna(row.get("price")):
        lines.append(f"<b>Price:</b> ${row.get('price'):,.0f}")
    if "days_on_market" in row.index and pd.notna(row.get("days_on_market")):
        lines.append(f"<b>Days on Market:</b> {int(row.get('days_on_market'))}")
    if "deal_score" in row.index and pd.notna(row.get("deal_score")):
        lines.append(f"<b>Deal Score:</b> {row.get('deal_score')}")
    if "id" in row.index and pd.notna(row.get("id")):
        lines.append(f"<b>ID:</b> {row.get('id')}")
    else:
        lines.append(f"<b>Index:</b> {row.name}")
    return "<br>".join(lines)


def _load_cache(cache_path: Path) -> dict[str, tuple[float, float] | tuple[float, float]]:
    if cache_path.exists():
        try:
            with cache_path.open("rb") as f:
                cache = pickle.load(f)
            if isinstance(cache, dict):
                return cache
        except (pickle.PickleError, EOFError, OSError):
            return {}
    return {}


def _save_cache(cache_path: Path, cache: dict[str, tuple[float, float] | tuple[float, float]]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("wb") as f:
        pickle.dump(cache, f, protocol=pickle.HIGHEST_PROTOCOL)


def _resolve_address_series(df: pd.DataFrame) -> pd.Series:
    if "address" in df.columns:
        return df["address"].astype(str).str.strip()

    if "location_address_line" in df.columns:
        line = df["location_address_line"].astype(str).str.strip()
        if "location_address_city" in df.columns and "location_address_state_code" in df.columns:
            city = df["location_address_city"].fillna("").astype(str).str.strip()
            state = df["location_address_state_code"].fillna("").astype(str).str.strip()
            return (line + ", " + city + ", " + state).str.strip(" ,")
        return line

    if "location_address_city" in df.columns and "location_address_state_code" in df.columns:
        city = df["location_address_city"].fillna("").astype(str).str.strip()
        state = df["location_address_state_code"].fillna("").astype(str).str.strip()
        return (city + ", " + state).str.strip(" ,")

    raise ValueError(
        "No address field found. Provide 'address' or 'location_address_line' "
        "(optionally with city/state columns)."
    )


def _geo_1304_i1_GET_detroit_map(df: pd.DataFrame):
    out_df = df.copy()
    cache_path = Path("data") / "geo_cache.pkl"
    geo_cache = _load_cache(cache_path)

    geolocator = Nominatim(user_agent="detroit_real_estate_mapper")
    geocode = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=1,
        max_retries=2,
        error_wait_seconds=2,
        swallow_exceptions=False,
    )

    address_series = _resolve_address_series(out_df)
    out_df["address"] = address_series
    unique_addresses = pd.Series(address_series.dropna().unique())
    missing_addresses = [a for a in unique_addresses if a and a not in geo_cache]

    for addr in tqdm(missing_addresses, desc="Geocoding", leave=False):
        query = f"{addr}, Detroit, MI"
        try:
            location = geocode(query)
            if location is None:
                geo_cache[addr] = (np.nan, np.nan)
            else:
                geo_cache[addr] = (float(location.latitude), float(location.longitude))
        except GEOPY_EXCEPTIONS + (ValueError, OSError):
            geo_cache[addr] = (np.nan, np.nan)

    _save_cache(cache_path, geo_cache)

    out_df["lat"] = address_series.map(lambda x: geo_cache.get(x, (np.nan, np.nan))[0] if x else np.nan)
    out_df["lon"] = address_series.map(lambda x: geo_cache.get(x, (np.nan, np.nan))[1] if x else np.nan)

    m = folium.Map(location=[42.33, -83.04], zoom_start=11, control_scale=True)
    marker_layer = folium.FeatureGroup(name="Markers", show=True)
    heat_layer = folium.FeatureGroup(name="HeatMap", show=True)
    cluster = MarkerCluster(name="Property Cluster", disableClusteringAtZoom=15)
    marker_layer.add_child(cluster)

    has_price = "price" in out_df.columns or "list_price" in out_df.columns
    price_col = "price" if "price" in out_df.columns else "list_price" if "list_price" in out_df.columns else None
    if price_col:
        out_df["price"] = _safe_numeric(out_df[price_col])
        has_price = True
    else:
        has_price = False

    has_deal_score = "deal_score" in out_df.columns
    if has_deal_score:
        out_df["deal_score"] = _safe_numeric(out_df["deal_score"])

    has_list_date = "list_date" in out_df.columns
    if has_list_date:
        out_df["list_date"] = pd.to_datetime(out_df["list_date"], errors="coerce", utc=True)
        out_df["days_on_market"] = (pd.Timestamp.now(tz="UTC") - out_df["list_date"]).dt.days
        out_df["days_on_market"] = _safe_numeric(out_df["days_on_market"])
    has_dom = "days_on_market" in out_df.columns and out_df["days_on_market"].notna().any()

    dom_norm = _normalize(out_df["days_on_market"]) if has_dom else pd.Series(np.nan, index=out_df.index)
    price_norm = _normalize(out_df["price"]) if has_price else pd.Series(np.nan, index=out_df.index)
    deal_norm = _normalize(out_df["deal_score"]) if has_deal_score else pd.Series(np.nan, index=out_df.index)

    valid_prices = out_df["price"].dropna() if has_price else pd.Series(dtype=float)
    top_expensive_idx = set(valid_prices.nlargest(5).index.tolist()) if not valid_prices.empty else set()
    top_cheap_idx = set(valid_prices.nsmallest(5).index.tolist()) if not valid_prices.empty else set()

    for idx, row in out_df.iterrows():
        lat = row.get("lat")
        lon = row.get("lon")
        if pd.isna(lat) or pd.isna(lon):
            continue

        is_top_expensive = idx in top_expensive_idx
        is_top_cheap = idx in top_cheap_idx

        if has_price and pd.notna(price_norm.loc[idx]):
            radius = float(4 + 8 * price_norm.loc[idx])
        else:
            radius = 6.0

        if is_top_expensive:
            color = "black"
            radius = max(radius, 12.0)
            label = "TOP EXPENSIVE"
        elif is_top_cheap:
            color = "purple"
            radius = max(radius, 12.0)
            label = "TOP CHEAP"
        elif has_dom and pd.notna(dom_norm.loc[idx]):
            color = _value_to_days_on_market_color(float(dom_norm.loc[idx]))
            label = None
        elif has_deal_score:
            color = _value_to_deal_color(float(deal_norm.loc[idx]) if pd.notna(deal_norm.loc[idx]) else np.nan)
            label = None
        elif has_price:
            color = _value_to_cheap_expensive_color(
                float(price_norm.loc[idx]) if pd.notna(price_norm.loc[idx]) else np.nan
            )
            label = None
        else:
            color = "#3498db"
            label = None

        popup_html = _popup_html(row, marker_label=label)

        folium.CircleMarker(
            location=[float(lat), float(lon)],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            weight=1,
            popup=folium.Popup(popup_html, max_width=350),
        ).add_to(cluster)

    geocoded = out_df.dropna(subset=["lat", "lon"]).copy()
    if not geocoded.empty:
        if has_price and geocoded["price"].notna().any():
            weights = geocoded["price"].fillna(0.0).astype(float)
            max_weight = max(weights.max(), 1.0)
            norm_weights = (weights / max_weight).clip(lower=0.0)
            heat_data = [
                [float(r.lat), float(r.lon), float(w)]
                for r, w in zip(geocoded.itertuples(), norm_weights.tolist())
            ]
        else:
            heat_data = [[float(r.lat), float(r.lon), 1.0] for r in geocoded.itertuples()]

        HeatMap(heat_data, radius=15, blur=20, min_opacity=0.2, max_zoom=15).add_to(heat_layer)

    legend_html = """
    <div style="
        position: fixed;
        bottom: 40px;
        left: 40px;
        z-index: 9999;
        background: white;
        border: 1px solid #bbb;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        line-height: 1.6;
    ">
      <div style="font-weight: 700; margin-bottom: 6px;">Legend — Days on Market</div>
      <div style="margin-bottom: 4px;">
        <span style="display:inline-block;width:12px;height:12px;background:#e74c3c;border-radius:50%;"></span>
        New listing
        &nbsp;→&nbsp;
        <span style="display:inline-block;width:12px;height:12px;background:#f1c40f;border-radius:50%;"></span>
        Mid
        &nbsp;→&nbsp;
        <span style="display:inline-block;width:12px;height:12px;background:#2ecc71;border-radius:50%;"></span>
        Sitting / Long time
      </div>
      <div><span style="color:black;">●</span> Black: Top 5 most expensive</div>
      <div><span style="color:purple;">●</span> Purple: Top 5 cheapest</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    marker_layer.add_to(m)
    heat_layer.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    m.save("detroit_properties_map.html")
    return out_df, m
