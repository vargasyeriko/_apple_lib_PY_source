# -----######----- ROBINHOOD AUDITABLE BALANCE FUNCTION -----######-----

from collections import defaultdict
import re

import pandas as pd
import yfinance as yf
from tqdm.auto import tqdm


def _rh_1607_i3_GET_df_balance(
    df_ledger: pd.DataFrame,
) -> pd.DataFrame:
    """
    Reconstruct current Robinhood cash and stock holdings.

    The function does NOT use the known Robinhood account balance.

    Inputs:
        df_ledger:
            Original Robinhood transaction DataFrame.

    Output:
        One-row DataFrame containing only:
            cash_holdings
            stock_holdings
    """

    df = df_ledger.copy()

    required_columns = {
        "date",
        "action",
        "ticker",
        "quantity",
        "amount",
        "note",
    }

    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing columns: {sorted(missing_columns)}"
        )

    df["_row_order"] = range(len(df))

    df["date"] = pd.to_datetime(
        df["date"],
        errors="raise",
    )

    df["action"] = (
        df["action"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["ticker"] = (
        df["ticker"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["note"] = (
        df["note"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce",
    ).fillna(0.0)

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce",
    ).fillna(0.0)

    df = (
        df.sort_values(["date", "_row_order"])
        .reset_index(drop=True)
    )

    # Official corporate actions missing from the transaction CSV.
    #
    # These are independent source facts—not values derived from
    # the current Robinhood account balance.
    corporate_actions = [
        {
            "date": pd.Timestamp("2022-10-27"),
            "kind": "cash_merger",
            "ticker": "Twitter",
            "cash_per_share": 54.20,
        },
        {
            "date": pd.Timestamp("2024-08-07"),
            "kind": "cancel",
            "ticker": "INVITAE",
        },
        {
            "date": pd.Timestamp("2024-09-13"),
            "kind": "cancel",
            "ticker": "2U",
        },
        {
            "date": pd.Timestamp("2024-10-01"),
            "kind": "spinoff",
            "parent": "TC Energy",
            "child": "South Bow",
            "ratio": 0.2,
        },
    ]

    event_stream = []

    for row in df.itertuples(index=False):
        event_stream.append(
            {
                "date": row.date,
                "priority": 0,
                "kind": "ledger",
                "row": row,
            }
        )

    for event in corporate_actions:
        event_stream.append(
            {
                "date": event["date"],
                "priority": 1,
                "kind": "corporate_action",
                "event": event,
            }
        )

    event_stream.sort(
        key=lambda event: (
            event["date"],
            event["priority"],
        )
    )

    shares = defaultdict(float)
    cash = 0.0

    for item in tqdm(
        event_stream,
        desc="Reconstructing Robinhood ledger",
    ):
        if item["kind"] == "ledger":

            row = item["row"]

            action = row.action
            ticker = row.ticker
            quantity = float(row.quantity)
            amount = float(row.amount)

            if action == "buy":
                shares[ticker] += quantity

            elif action == "sell":
                shares[ticker] -= quantity

            elif action == "split":

                ratio_match = re.search(
                    r"(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)",
                    row.note,
                )

                if not ratio_match:
                    raise ValueError(
                        f"Cannot parse split ratio: {row.note}"
                    )

                numerator = float(ratio_match.group(1))
                denominator = float(ratio_match.group(2))

                shares[ticker] *= numerator / denominator

            # Bonus stock is not a cash deposit.
            # Its quantity and actual ticker are missing in this CSV.
            if action not in {"bonus", "split"}:
                cash += amount

        else:

            event = item["event"]
            kind = event["kind"]

            if kind == "cash_merger":

                ticker = event["ticker"]

                cash += (
                    shares[ticker]
                    * event["cash_per_share"]
                )

                shares[ticker] = 0.0

            elif kind == "cancel":

                shares[event["ticker"]] = 0.0

            elif kind == "spinoff":

                shares[event["child"]] += (
                    shares[event["parent"]]
                    * event["ratio"]
                )

    # Remove tiny rounding remnants, such as South Bow's 0.0000002.
    shares = {
        ticker: quantity
        for ticker, quantity in shares.items()
        if abs(quantity) >= 1e-6
    }

    symbol_map = {
        "DOGE": "DOGE-USD",
        "Netflix": "NFLX",
        "Alibaba": "BABA",
        "NVIDIA": "NVDA",
        "LendingTree": "TREE",
        "Ford": "F",
        "Apple": "AAPL",
        "TC Energy": "TRP",
        "South Bow": "SOBO",
        "AMD": "AMD",
        "ASML": "ASML",
        "Broadcom": "AVGO",
    }

    stock_holdings = 0.0

    for ticker, quantity in tqdm(
        shares.items(),
        total=len(shares),
        desc="Fetching current prices",
    ):
        if ticker not in symbol_map:
            raise ValueError(
                f"No verified market symbol for active holding: {ticker}"
            )

        symbol = symbol_map[ticker]

        history = yf.Ticker(symbol).history(
            period="5d",
            interval="1d",
            auto_adjust=False,
        )

        closing_prices = history["Close"].dropna()

        if closing_prices.empty:
            raise ValueError(
                f"No current price available for {ticker} ({symbol})"
            )

        latest_price = float(closing_prices.iloc[-1])

        stock_holdings += quantity * latest_price

    df_balance = pd.DataFrame(
        {
            "cash_holdings": [round(cash, 2)],
            "stock_holdings": [round(stock_holdings, 2)],
        }
    )

    return df_balance


# -----######----- ROBINHOOD MONTHLY BALANCE FUNCTION -----######-----
# -----######----- ROBINHOOD MONTHLY AUDIT FUNCTION -----######-----

import re
from collections import defaultdict

import pandas as pd
import requests
import yfinance as yf
from tqdm.auto import tqdm


def _rh_1607_i5_GET_df_monthly(
    df_ledger: pd.DataFrame,
    end_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Calculate Robinhood balances on the first U.S. trading session
    of every month.

    Returns exactly:
        cash_holdings
        stock_holdings

    Method:
        - Reconstruct cash and shares chronologically.
        - Apply ledger splits to share quantities.
        - Apply verified external corporate actions.
        - Use raw historical closing prices.
        - Never use the known Robinhood balance as an input.
        - Never interpolate missing security prices.
    """

    df = df_ledger.copy()

    required_columns = {
        "date",
        "action",
        "ticker",
        "quantity",
        "amount",
        "note",
    }

    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing columns: {sorted(missing_columns)}"
        )

    # ---------------------------------------------------------
    # CLEAN LEDGER
    # ---------------------------------------------------------

    df["_order"] = range(len(df))

    df["date"] = pd.to_datetime(
        df["date"],
        errors="raise",
    ).dt.normalize()

    df["action"] = (
        df["action"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["ticker"] = (
        df["ticker"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["note"] = (
        df["note"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce",
    ).fillna(0.0)

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce",
    ).fillna(0.0)

    df = (
        df.sort_values(["date", "_order"])
        .reset_index(drop=True)
    )

    end_date = (
        df["date"].max()
        if end_date is None
        else pd.Timestamp(end_date).normalize()
    )

    fetch_start = (
        df["date"].min().to_period("M").start_time
        - pd.Timedelta(days=10)
    )

    fetch_end = end_date + pd.Timedelta(days=10)

    # ---------------------------------------------------------
    # VERIFIED MARKET SYMBOLS
    # ---------------------------------------------------------

    symbol_map = {
        "DOGE": "DOGE-USD",
        "Twitter": "TWTR",
        "Netflix": "NFLX",
        "Alibaba": "BABA",
        "NVIDIA": "NVDA",
        "INVITAE": "NVTA",
        "LendingTree": "TREE",
        "2U": "TWOU",
        "Ford": "F",
        "Apple": "AAPL",
        "TC Energy": "TRP",
        "South Bow": "SOBO",
        "AMD": "AMD",
        "ASML": "ASML",
        "Broadcom": "AVGO",
    }

    nasdaq_fallback = {
        "Twitter": "TWTR",
        "INVITAE": "NVTA",
        "2U": "TWOU",
    }

    # ---------------------------------------------------------
    # CORPORATE ACTIONS ABSENT FROM THE CSV
    # ---------------------------------------------------------

    corporate_actions = [
        {
            "date": pd.Timestamp("2022-10-27"),
            "kind": "cash_merger",
            "ticker": "Twitter",
            "cash_per_share": 54.20,
        },
        {
            "date": pd.Timestamp("2024-08-07"),
            "kind": "cancel",
            "ticker": "INVITAE",
        },
        {
            "date": pd.Timestamp("2024-09-13"),
            "kind": "cancel",
            "ticker": "2U",
        },
        {
            "date": pd.Timestamp("2024-10-01"),
            "kind": "spinoff",
            "parent": "TC Energy",
            "child": "South Bow",
            "ratio": 0.2,
        },
    ]

    # ---------------------------------------------------------
    # PRICE HELPERS
    # ---------------------------------------------------------

    def _empty_close() -> pd.Series:
        """
        Empty price Series with the correct datetime index.

        This specifically prevents:
            RangeIndex < Timestamp
        """

        return pd.Series(
            index=pd.DatetimeIndex([], name="Date"),
            dtype="float64",
            name="Close",
        )

    def _normalize_close(
        close: pd.Series,
    ) -> pd.Series:
        """
        Ensure every price Series has a clean DatetimeIndex.
        """

        if close is None or len(close) == 0:
            return _empty_close()

        close = pd.to_numeric(
            close,
            errors="coerce",
        ).dropna().astype(float)

        if close.empty:
            return _empty_close()

        datetime_index = pd.to_datetime(
            close.index,
            errors="coerce",
        )

        valid_dates = ~datetime_index.isna()

        close = close.iloc[valid_dates].copy()

        datetime_index = pd.DatetimeIndex(
            datetime_index[valid_dates]
        )

        if datetime_index.tz is not None:
            datetime_index = datetime_index.tz_localize(None)

        close.index = datetime_index.normalize()

        return (
            close.groupby(level=0)
            .last()
            .sort_index()
        )

    def _fetch_yahoo_raw(
        symbol: str,
    ) -> pd.Series:
        """
        Retrieve raw historical Close from Yahoo.

        auto_adjust=False is intentional:
        share quantities already account for splits.
        """

        try:
            history = yf.Ticker(symbol).history(
                start=fetch_start.strftime("%Y-%m-%d"),
                end=fetch_end.strftime("%Y-%m-%d"),
                interval="1d",
                auto_adjust=False,
                actions=False,
                repair=False,
                raise_errors=False,
            )

        except Exception:
            return _empty_close()

        if history.empty or "Close" not in history.columns:
            return _empty_close()

        return _normalize_close(
            history["Close"]
        )

    def _fetch_nasdaq_raw(
        symbol: str,
    ) -> pd.Series:
        """
        Attempt raw Nasdaq historical prices for delisted equities.
        """

        url = (
            f"https://api.nasdaq.com/api/quote/"
            f"{symbol}/historical"
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 "
                "Chrome/126 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.nasdaq.com",
            "Referer": "https://www.nasdaq.com/",
        }

        parameters = {
            "assetclass": "stocks",
            "fromdate": fetch_start.strftime("%m/%d/%Y"),
            "todate": fetch_end.strftime("%m/%d/%Y"),
            "limit": 5000,
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                params=parameters,
                timeout=30,
            )

            response.raise_for_status()

            payload = response.json()

            rows = (
                (payload.get("data") or {})
                .get("tradesTable", {})
                .get("rows", [])
            )

        except Exception:
            return _empty_close()

        if not rows:
            return _empty_close()

        df_prices = pd.DataFrame(rows)

        required_price_columns = {
            "date",
            "close",
        }

        if not required_price_columns.issubset(
            df_prices.columns
        ):
            return _empty_close()

        close_values = pd.to_numeric(
            df_prices["close"]
            .astype(str)
            .str.replace(
                r"[$,]",
                "",
                regex=True,
            ),
            errors="coerce",
        )

        close = pd.Series(
            close_values.to_numpy(),
            index=pd.to_datetime(
                df_prices["date"],
                errors="coerce",
            ),
            name="Close",
        )

        return _normalize_close(close)

    def _fetch_raw_close(
        ticker: str,
    ) -> pd.Series:
        """
        Yahoo first, then Nasdaq for specified delisted stocks.
        """

        symbol = symbol_map[ticker]

        close = _fetch_yahoo_raw(symbol)

        if close.empty and ticker in nasdaq_fallback:
            close = _fetch_nasdaq_raw(
                nasdaq_fallback[ticker]
            )

        return close

    # ---------------------------------------------------------
    # FIRST U.S. TRADING SESSION EACH MONTH
    # ---------------------------------------------------------

    market_close = _fetch_yahoo_raw("SPY")

    if market_close.empty:
        raise RuntimeError(
            "Could not retrieve SPY market-session dates."
        )

    # Account opened during April 2022, so May 2022 is the
    # first complete first-of-month valuation.
    first_period = (
        df["date"].min()
        + pd.offsets.MonthBegin(1)
    ).to_period("M")

    monthly_periods = pd.period_range(
        first_period,
        end_date.to_period("M"),
        freq="M",
    )

    valuation_dates = []

    for period in monthly_periods:

        sessions = market_close.index[
            market_close.index.to_period("M")
            == period
        ]

        sessions = sessions[
            sessions <= end_date
        ]

        if len(sessions) > 0:
            valuation_dates.append(
                pd.Timestamp(sessions[0])
            )

    # ---------------------------------------------------------
    # CREATE EVENT STREAM
    # ---------------------------------------------------------

    events = []

    for row in tqdm(
        df.itertuples(index=False),
        total=len(df),
        desc="Reading ledger",
    ):
        events.append(
            {
                "date": row.date,
                "priority": 0,
                "type": "ledger",
                "payload": row,
            }
        )

    for event in corporate_actions:

        if event["date"] <= end_date:
            events.append(
                {
                    "date": event["date"],
                    "priority": 1,
                    "type": "corporate",
                    "payload": event,
                }
            )

    events.sort(
        key=lambda event: (
            event["date"],
            event["priority"],
        )
    )

    # ---------------------------------------------------------
    # RECONSTRUCT MONTHLY CASH AND SHARES
    # ---------------------------------------------------------

    shares = defaultdict(float)
    cash = 0.0
    event_index = 0
    snapshots = []

    def _apply_event(
        event: dict,
    ) -> None:

        nonlocal cash

        payload = event["payload"]

        if event["type"] == "ledger":

            action = payload.action
            ticker = payload.ticker
            quantity = float(payload.quantity)
            amount = float(payload.amount)

            if action == "buy":
                shares[ticker] += quantity

            elif action == "sell":
                shares[ticker] -= quantity

            elif action == "split":

                ratio_match = re.search(
                    r"(\d+(?:\.\d+)?)"
                    r"\s*:\s*"
                    r"(\d+(?:\.\d+)?)",
                    payload.note,
                )

                if not ratio_match:
                    raise ValueError(
                        f"Cannot parse split ratio for "
                        f"{ticker}: {payload.note}"
                    )

                numerator = float(
                    ratio_match.group(1)
                )

                denominator = float(
                    ratio_match.group(2)
                )

                shares[ticker] *= (
                    numerator / denominator
                )

            elif action not in {
                "deposit",
                "withdrawal",
                "dividend",
                "fee",
                "bonus",
            }:
                raise ValueError(
                    f"Unsupported action: {action}"
                )

            # Buys, sells, dividends, deposits, withdrawals
            # and fees use their recorded ledger amounts.
            #
            # Bonus is excluded because the actual stock ticker
            # and quantity are missing.
            if action not in {
                "bonus",
                "split",
            }:
                cash += amount

        else:

            kind = payload["kind"]

            if kind == "cash_merger":

                ticker = payload["ticker"]

                cash += (
                    shares[ticker]
                    * payload["cash_per_share"]
                )

                shares[ticker] = 0.0

            elif kind == "cancel":

                shares[
                    payload["ticker"]
                ] = 0.0

            elif kind == "spinoff":

                shares[
                    payload["child"]
                ] += (
                    shares[payload["parent"]]
                    * payload["ratio"]
                )

    for valuation_date in tqdm(
        valuation_dates,
        desc="Building monthly snapshots",
    ):

        while (
            event_index < len(events)
            and events[event_index]["date"]
            <= valuation_date
        ):
            _apply_event(
                events[event_index]
            )

            event_index += 1

        snapshots.append(
            {
                "valuation_date": valuation_date,
                "cash_holdings": cash,
                "shares": {
                    ticker: quantity
                    for ticker, quantity
                    in shares.items()
                    if abs(quantity) >= 1e-8
                },
            }
        )

    # ---------------------------------------------------------
    # FETCH ONLY PRICES ACTUALLY NEEDED
    # ---------------------------------------------------------

    required_tickers = sorted(
        {
            ticker
            for snapshot in snapshots
            for ticker in snapshot["shares"]
        }
    )

    prices = {}

    for ticker in tqdm(
        required_tickers,
        desc="Fetching historical prices",
    ):

        if ticker not in symbol_map:
            raise ValueError(
                f"No verified market symbol for "
                f"active holding: {ticker}"
            )

        close = _fetch_raw_close(ticker)

        if close.empty:
            raise RuntimeError(
                f"No historical prices found for "
                f"{ticker} ({symbol_map[ticker]}). "
                f"No value was estimated or interpolated."
            )

        prices[ticker] = close

    # ---------------------------------------------------------
    # VALUE MONTHLY SNAPSHOTS
    # ---------------------------------------------------------

    output_rows = []

    for snapshot in tqdm(
        snapshots,
        desc="Valuing monthly balances",
    ):

        valuation_date = snapshot[
            "valuation_date"
        ]

        stock_holdings = 0.0

        for ticker, quantity in (
            snapshot["shares"].items()
        ):

            close = prices[ticker]

            available_prices = close.loc[
                close.index <= valuation_date
            ]

            if available_prices.empty:
                raise RuntimeError(
                    f"No price on or before "
                    f"{valuation_date.date()} "
                    f"for {ticker}."
                )

            price_date = (
                available_prices.index[-1]
            )

            age_days = (
                valuation_date - price_date
            ).days

            if age_days > 7:
                raise RuntimeError(
                    f"Stale price for {ticker}: "
                    f"{price_date.date()} used for "
                    f"{valuation_date.date()}."
                )

            latest_price = float(
                available_prices.iloc[-1]
            )

            stock_holdings += (
                quantity * latest_price
            )

        output_rows.append(
            {
                "valuation_date": valuation_date,
                "cash_holdings": round(
                    snapshot["cash_holdings"],
                    2,
                ),
                "stock_holdings": round(
                    stock_holdings,
                    2,
                ),
            }
        )

    df_monthly = (
        pd.DataFrame(output_rows)
        .set_index("valuation_date")
        [
            [
                "cash_holdings",
                "stock_holdings",
            ]
        ]
    )

    df_monthly.attrs[
        "known_balance_used_as_input"
    ] = False

    df_monthly.attrs[
        "price_method"
    ] = (
        "Raw historical close. Yahoo first; "
        "Nasdaq fallback for selected delisted equities. "
        "No interpolation."
    )

    df_monthly.attrs[
        "bonus_excluded"
    ] = (
        "The $5.50 bonus stock lacks a verified "
        "ticker and quantity."
    )

    return df_monthly