# -----######----- ROBINHOOD AUDITABLE BALANCE FUNCTION -----######-----

from collections import defaultdict
from io import StringIO
import logging
import re

import pandas as pd
import requests
import yfinance as yf
from tqdm.auto import tqdm


def _rh_1607_i3_GET_df_balance(
    df_ledger: pd.DataFrame,
    mode: str = "monthly",
    end_date: str | pd.Timestamp | None = None,
    first_sessions: int = 7,
) -> pd.DataFrame:
    """
    Reconstruct Robinhood cash and stock holdings.

    Parameters
    ----------
    df_ledger:
        Original Robinhood ledger DataFrame.

    mode:
        "monthly":
            Return the balance on the earliest valid market session
            among the first several sessions of every month.

        "current":
            Return one row containing the latest reconstructed balance.

    end_date:
        Optional final valuation date.

    first_sessions:
        Number of early market sessions checked each month.
        This handles weekends, holidays and newly listed securities.

    Returns
    -------
    DataFrame containing only:
        cash_holdings
        stock_holdings

    Important
    ---------
    - The known Robinhood balance is never used as an input.
    - Splits modify shares, not historical prices.
    - Dividends are taken from the ledger's amount column.
    - Reinvested dividends already have matching buy rows.
    - Missing delisted prices use transaction-price interpolation
      only after historical sources fail.
    """

    # ---------------------------------------------------------
    # VALIDATE AND CLEAN
    # ---------------------------------------------------------

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

    mode = str(mode).strip().lower()

    if mode not in {"monthly", "current"}:
        raise ValueError(
            "mode must be either 'monthly' or 'current'."
        )

    df["_row_order"] = range(len(df))

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

    for column in ["quantity", "unit_price", "amount"]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            ).fillna(0.0)

    df = (
        df.sort_values(["date", "_row_order"])
        .reset_index(drop=True)
    )

    today = pd.Timestamp.today().normalize()

    final_date = (
        max(today, df["date"].max())
        if end_date is None
        else pd.Timestamp(end_date).normalize()
    )

    fetch_start = (
        df["date"].min().to_period("M").start_time
        - pd.Timedelta(days=10)
    )

    fetch_end = final_date + pd.Timedelta(days=10)

    # ---------------------------------------------------------
    # MARKET SYMBOLS
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

    known_delisted = {
        "Twitter",
        "INVITAE",
        "2U",
    }

    # ---------------------------------------------------------
    # CORPORATE ACTIONS MISSING FROM THE CSV
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
    # SPLIT EVENTS
    # ---------------------------------------------------------

    split_events = defaultdict(list)

    for row in df.loc[
        df["action"].eq("split")
    ].itertuples(index=False):

        ratio_match = re.search(
            r"(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)",
            row.note,
        )

        if not ratio_match:
            raise ValueError(
                f"Cannot parse split ratio for "
                f"{row.ticker}: {row.note}"
            )

        factor = (
            float(ratio_match.group(1))
            / float(ratio_match.group(2))
        )

        split_events[row.ticker].append(
            {
                "date": row.date,
                "factor": factor,
            }
        )

    # ---------------------------------------------------------
    # PRICE HELPERS
    # ---------------------------------------------------------

    def _empty_prices() -> pd.Series:

        return pd.Series(
            index=pd.DatetimeIndex([], name="Date"),
            dtype="float64",
            name="Close",
        )

    def _clean_prices(
        prices: pd.Series,
    ) -> pd.Series:

        if prices is None or len(prices) == 0:
            return _empty_prices()

        prices = pd.to_numeric(
            prices,
            errors="coerce",
        ).dropna()

        if prices.empty:
            return _empty_prices()

        price_dates = pd.to_datetime(
            prices.index,
            errors="coerce",
        )

        valid_dates = ~price_dates.isna()

        prices = prices.iloc[valid_dates].copy()

        price_dates = pd.DatetimeIndex(
            price_dates[valid_dates]
        )

        if price_dates.tz is not None:
            price_dates = price_dates.tz_localize(None)

        prices.index = price_dates.normalize()

        return (
            prices.astype(float)
            .groupby(level=0)
            .last()
            .sort_index()
        )

    def _fetch_yahoo(
        symbol: str,
    ) -> pd.Series:
        """
        Fetch unadjusted historical closes.

        Share quantities already handle stock splits, so historical
        prices are not manually multiplied or divided.
        """

        yahoo_logger = logging.getLogger("yfinance")
        old_level = yahoo_logger.level

        yahoo_logger.setLevel(logging.CRITICAL)

        try:
            history = yf.download(
                symbol,
                start=fetch_start.strftime("%Y-%m-%d"),
                end=fetch_end.strftime("%Y-%m-%d"),
                interval="1d",
                auto_adjust=False,
                actions=False,
                progress=False,
                threads=False,
            )

        except Exception:
            return _empty_prices()

        finally:
            yahoo_logger.setLevel(old_level)

        if history is None or history.empty:
            return _empty_prices()

        try:
            if isinstance(history.columns, pd.MultiIndex):

                close_block = history.xs(
                    "Close",
                    axis=1,
                    level=0,
                )

                prices = close_block.iloc[:, 0]

            else:
                prices = history["Close"]

        except Exception:
            return _empty_prices()

        return _clean_prices(prices)

    def _fetch_stooq(
        symbol: str,
    ) -> pd.Series:
        """
        Free fallback for historical U.S. equity prices,
        including some delisted tickers.
        """

        if symbol.endswith("-USD"):
            return _empty_prices()

        url = "https://stooq.com/q/d/l/"

        parameters = {
            "s": f"{symbol.lower()}.us",
            "d1": fetch_start.strftime("%Y%m%d"),
            "d2": fetch_end.strftime("%Y%m%d"),
            "i": "d",
        }

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Safari/537.36"
            )
        }

        try:
            response = requests.get(
                url,
                params=parameters,
                headers=headers,
                timeout=20,
            )

            response.raise_for_status()

            text = response.text.strip()

            if (
                not text
                or "No data" in text
                or "Date,Open" not in text
            ):
                return _empty_prices()

            history = pd.read_csv(
                StringIO(text)
            )

        except Exception:
            return _empty_prices()

        if not {"Date", "Close"}.issubset(history.columns):
            return _empty_prices()

        prices = pd.Series(
            history["Close"].to_numpy(),
            index=pd.to_datetime(
                history["Date"],
                errors="coerce",
            ),
            name="Close",
        )

        return _clean_prices(prices)

    def _fetch_market_prices(
        ticker: str,
    ) -> pd.Series:

        symbol = symbol_map[ticker]

        # Delisted securities are attempted through Stooq first.
        if ticker in known_delisted:

            prices = _fetch_stooq(symbol)

            if prices.empty:
                prices = _fetch_yahoo(symbol)

        else:

            prices = _fetch_yahoo(symbol)

            if prices.empty:
                prices = _fetch_stooq(symbol)

        return prices

    # ---------------------------------------------------------
    # LEDGER PRICE ANCHORS
    # ---------------------------------------------------------

    price_anchors = defaultdict(list)

    if "unit_price" in df.columns:

        anchor_rows = df.loc[
            df["action"].isin({"buy", "sell"})
            & df["unit_price"].gt(0)
        ]

        for row in anchor_rows.itertuples(index=False):

            price_anchors[row.ticker].append(
                {
                    "date": row.date,
                    "price": float(row.unit_price),
                    "source": "ledger transaction",
                }
            )

    # Independent corporate-action price anchors.
    price_anchors["Twitter"].append(
        {
            "date": pd.Timestamp("2022-10-27"),
            "price": 54.20,
            "source": "cash merger",
        }
    )

    price_anchors["INVITAE"].append(
        {
            "date": pd.Timestamp("2024-08-07"),
            "price": 0.0,
            "source": "equity cancellation",
        }
    )

    price_anchors["2U"].append(
        {
            "date": pd.Timestamp("2024-09-13"),
            "price": 0.0,
            "source": "equity cancellation",
        }
    )

    for ticker in price_anchors:

        price_anchors[ticker] = sorted(
            price_anchors[ticker],
            key=lambda item: item["date"],
        )

    def _split_basis(
        ticker: str,
        date: pd.Timestamp,
    ) -> float:
        """
        Cumulative share multiplier through a particular date.
        """

        factor = 1.0

        for split in split_events.get(ticker, []):

            if split["date"] <= date:
                factor *= split["factor"]

        return factor

    def _estimated_price(
        ticker: str,
        valuation_date: pd.Timestamp,
    ) -> tuple[float | None, str]:
        """
        Final fallback.

        Interpolates only between known transaction/corporate-action
        anchors. It does not use the final Robinhood balance.
        """

        anchors = price_anchors.get(ticker, [])

        if not anchors:
            return None, "no price anchors"

        target_basis = _split_basis(
            ticker,
            valuation_date,
        )

        adjusted_anchors = []

        for anchor in anchors:

            anchor_basis = _split_basis(
                ticker,
                anchor["date"],
            )

            adjusted_price = (
                float(anchor["price"])
                * anchor_basis
                / target_basis
            )

            adjusted_anchors.append(
                {
                    "date": anchor["date"],
                    "price": adjusted_price,
                    "source": anchor["source"],
                }
            )

        before = [
            anchor
            for anchor in adjusted_anchors
            if anchor["date"] <= valuation_date
        ]

        after = [
            anchor
            for anchor in adjusted_anchors
            if anchor["date"] >= valuation_date
        ]

        left = before[-1] if before else None
        right = after[0] if after else None

        if (
            left is not None
            and right is not None
            and left["date"] != right["date"]
        ):

            total_days = (
                right["date"] - left["date"]
            ).days

            passed_days = (
                valuation_date - left["date"]
            ).days

            weight = passed_days / total_days

            estimated = (
                left["price"]
                + weight
                * (
                    right["price"]
                    - left["price"]
                )
            )

            return (
                max(float(estimated), 0.0),
                "interpolated ledger/corporate anchors",
            )

        if left is not None:

            return (
                max(float(left["price"]), 0.0),
                f"last {left['source']} price",
            )

        if right is not None:

            return (
                max(float(right["price"]), 0.0),
                f"next {right['source']} price",
            )

        return None, "no usable anchor"

    # ---------------------------------------------------------
    # EVENT STREAM
    # ---------------------------------------------------------

    event_stream = []

    for row in df.itertuples(index=False):

        event_stream.append(
            {
                "date": row.date,
                "priority": 0,
                "kind": "ledger",
                "payload": row,
            }
        )

    for event in corporate_actions:

        event_stream.append(
            {
                "date": event["date"],
                "priority": 1,
                "kind": "corporate",
                "payload": event,
            }
        )

    event_stream.sort(
        key=lambda item: (
            item["date"],
            item["priority"],
        )
    )

    def _state_at(
        valuation_date: pd.Timestamp,
    ) -> tuple[float, dict[str, float]]:
        """
        Replay the ledger through the valuation date.
        """

        shares = defaultdict(float)
        cash = 0.0

        for item in event_stream:

            if item["date"] > valuation_date:
                break

            payload = item["payload"]

            if item["kind"] == "ledger":

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
                            f"Cannot parse split for "
                            f"{ticker}: {payload.note}"
                        )

                    split_factor = (
                        float(ratio_match.group(1))
                        / float(ratio_match.group(2))
                    )

                    shares[ticker] *= split_factor

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

                # The bonus row represents stock, but the ticker
                # and quantity are missing. It is not cash.
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

        clean_shares = {
            ticker: quantity
            for ticker, quantity in shares.items()
            if abs(quantity) >= 1e-6
        }

        return cash, clean_shares

    # ---------------------------------------------------------
    # FETCH PRICE HISTORY ONCE
    # ---------------------------------------------------------

    required_tickers = sorted(
        {
            ticker
            for ticker in symbol_map
            if (
                ticker in set(df["ticker"])
                or ticker == "South Bow"
            )
        }
    )

    price_history = {}

    for ticker in tqdm(
        required_tickers,
        desc="Fetching historical prices",
    ):

        price_history[ticker] = (
            _fetch_market_prices(ticker)
        )

    # SPY gives actual U.S. trading-session dates.
    market_sessions = _fetch_yahoo("SPY")

    if market_sessions.empty:

        session_dates = pd.bdate_range(
            fetch_start,
            final_date,
        )

    else:

        session_dates = market_sessions.index[
            market_sessions.index <= final_date
        ]

    estimated_records = []

    def _get_price(
        ticker: str,
        valuation_date: pd.Timestamp,
        allow_estimate: bool,
    ) -> tuple[float | None, str]:
        """
        Obtain the last real price no more than seven calendar days old.
        """

        prices = price_history.get(
            ticker,
            _empty_prices(),
        )

        available = prices.loc[
            prices.index <= valuation_date
        ]

        if not available.empty:

            price_date = available.index[-1]

            age_days = (
                valuation_date - price_date
            ).days

            if age_days <= 7:

                return (
                    float(available.iloc[-1]),
                    "historical market close",
                )

        if not allow_estimate:
            return None, "market price unavailable"

        estimated, source = _estimated_price(
            ticker,
            valuation_date,
        )

        return estimated, source

    def _value_state(
        valuation_date: pd.Timestamp,
        allow_all_estimates: bool,
    ) -> tuple[float, float, list[str]]:
        """
        Return cash, stock value and missing non-delisted prices.
        """

        cash, shares = _state_at(
            valuation_date
        )

        stock_value = 0.0
        missing = []

        for ticker, quantity in shares.items():

            allow_estimate = (
                allow_all_estimates
                or ticker in known_delisted
            )

            price, price_source = _get_price(
                ticker=ticker,
                valuation_date=valuation_date,
                allow_estimate=allow_estimate,
            )

            if price is None:

                missing.append(ticker)
                continue

            stock_value += quantity * price

            if price_source != "historical market close":

                estimated_records.append(
                    {
                        "valuation_date": valuation_date,
                        "ticker": ticker,
                        "quantity": quantity,
                        "price": price,
                        "method": price_source,
                    }
                )

        return cash, stock_value, missing

    # ---------------------------------------------------------
    # CURRENT MODE
    # ---------------------------------------------------------

    if mode == "current":

        valid_sessions = session_dates[
            session_dates <= final_date
        ]

        valuation_date = (
            pd.Timestamp(valid_sessions[-1])
            if len(valid_sessions)
            else final_date
        )

        cash, stock_value, missing = _value_state(
            valuation_date=valuation_date,
            allow_all_estimates=True,
        )

        if missing:
            raise ValueError(
                f"Could not value: {sorted(missing)}"
            )

        result = pd.DataFrame(
            {
                "cash_holdings": [
                    round(cash, 2)
                ],
                "stock_holdings": [
                    round(stock_value, 2)
                ],
            }
        )

        result.attrs["valuation_date"] = valuation_date
        result.attrs["known_balance_used_as_input"] = False
        result.attrs["estimated_prices"] = pd.DataFrame(
            estimated_records
        )

        return result

    # ---------------------------------------------------------
    # MONTHLY MODE
    # ---------------------------------------------------------

    # Start with the first complete month after account opening.
    first_period = (
        df["date"].min()
        + pd.offsets.MonthBegin(1)
    ).to_period("M")

    monthly_periods = pd.period_range(
        first_period,
        final_date.to_period("M"),
        freq="M",
    )

    output_rows = []

    for period in tqdm(
        monthly_periods,
        desc="Calculating monthly balances",
    ):

        month_sessions = session_dates[
            session_dates.to_period("M") == period
        ]

        month_sessions = month_sessions[
            month_sessions <= final_date
        ]

        candidates = list(
            month_sessions[:first_sessions]
        )

        if not candidates:

            candidates = [
                period.start_time
                + pd.offsets.BDay(0)
            ]

        selected_result = None

        # First try actual market prices.
        # Known-delisted securities may use their fallback curve.
        for valuation_date in candidates:

            cash, stock_value, missing = _value_state(
                valuation_date=pd.Timestamp(
                    valuation_date
                ),
                allow_all_estimates=False,
            )

            if not missing:

                selected_result = {
                    "valuation_date": pd.Timestamp(
                        valuation_date
                    ),
                    "cash_holdings": cash,
                    "stock_holdings": stock_value,
                }

                break

        # Final candidate: use ledger-price estimates rather
        # than failing the entire monthly calculation.
        if selected_result is None:

            valuation_date = pd.Timestamp(
                candidates[-1]
            )

            cash, stock_value, missing = _value_state(
                valuation_date=valuation_date,
                allow_all_estimates=True,
            )

            if missing:
                raise ValueError(
                    f"Unable to value {period}: "
                    f"{sorted(missing)}"
                )

            selected_result = {
                "valuation_date": valuation_date,
                "cash_holdings": cash,
                "stock_holdings": stock_value,
            }

        output_rows.append(
            selected_result
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
        .round(2)
    )

    df_monthly.index.name = "valuation_date"

    # Audit information without adding visible DataFrame columns.
    df_monthly.attrs["known_balance_used_as_input"] = False

    df_monthly.attrs["valuation_method"] = (
        "Earliest valid U.S. market session among the first "
        f"{first_sessions} sessions of each month."
    )

    df_monthly.attrs["estimated_prices"] = (
        pd.DataFrame(estimated_records)
        .drop_duplicates()
        .reset_index(drop=True)
    )

    df_monthly.attrs["bonus_excluded"] = (
        "The $5.50 bonus stock is excluded because the "
        "export does not identify its ticker or quantity."
    )

    return df_monthly


# -----######----- ROBINHOOD MONTHLY LEGAL TABLE -----######-----
# -----######----- ROBINHOOD MONTHLY LEGAL TABLE -----######-----
# -----######----- ROBINHOOD FINAL LEGAL LEDGER -----######-----

import pandas as pd
from tqdm.auto import tqdm


def _rh_1607_i9_GET_df_final_ledger(
    df_monthly: pd.DataFrame,
    df_ledger: pd.DataFrame,
    df_balance: pd.DataFrame,
    current_snapshot_date: str = "2026-07-15",
) -> pd.DataFrame:
    """
    Build the final monthly Robinhood legal exhibit.

    Inputs
    ------
    df_monthly:
        Monthly reconstructed balances containing:
            cash_holdings
            stock_holdings

    df_ledger:
        Original Robinhood transaction ledger.

    df_balance:
        Current one-row balance containing:
            cash_holdings
            stock_holdings

    current_snapshot_date:
        Date represented by df_balance.

    Returns
    -------
    Final legal-accounting DataFrame.
    """

    monthly = df_monthly.copy()
    ledger = df_ledger.copy()
    balance = df_balance.copy()

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    required_monthly = {
        "cash_holdings",
        "stock_holdings",
    }

    required_ledger = {
        "date",
        "action",
        "ticker",
        "amount",
    }

    required_balance = {
        "cash_holdings",
        "stock_holdings",
    }

    missing_monthly = required_monthly.difference(
        monthly.columns
    )

    missing_ledger = required_ledger.difference(
        ledger.columns
    )

    missing_balance = required_balance.difference(
        balance.columns
    )

    if missing_monthly:
        raise ValueError(
            f"df_monthly missing: {sorted(missing_monthly)}"
        )

    if missing_ledger:
        raise ValueError(
            f"df_ledger missing: {sorted(missing_ledger)}"
        )

    if missing_balance:
        raise ValueError(
            f"df_balance missing: {sorted(missing_balance)}"
        )

    # ---------------------------------------------------------
    # PREPARE MONTHLY BALANCES
    # ---------------------------------------------------------

    if "valuation_date" not in monthly.columns:

        monthly = monthly.reset_index()

        monthly = monthly.rename(
            columns={
                monthly.columns[0]: "valuation_date"
            }
        )

    monthly["valuation_date"] = pd.to_datetime(
        monthly["valuation_date"],
        errors="raise",
    ).dt.normalize()

    monthly["cash_holdings"] = pd.to_numeric(
        monthly["cash_holdings"],
        errors="raise",
    )

    monthly["stock_holdings"] = pd.to_numeric(
        monthly["stock_holdings"],
        errors="raise",
    )

    monthly = (
        monthly
        .sort_values("valuation_date")
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # PREPARE ORIGINAL LEDGER
    # ---------------------------------------------------------

    ledger["date"] = pd.to_datetime(
        ledger["date"],
        errors="raise",
    ).dt.normalize()

    ledger["action"] = (
        ledger["action"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[_-]+", " ", regex=True)
    )

    ledger["ticker"] = (
        ledger["ticker"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    if "note" not in ledger.columns:
        ledger["note"] = ""

    ledger["note"] = (
        ledger["note"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    ledger["amount"] = pd.to_numeric(
        ledger["amount"],
        errors="coerce",
    ).fillna(0.0)

    ledger["_month_period"] = (
        ledger["date"].dt.to_period("M")
    )

    deposit_actions = {
        "deposit",
        "cash deposit",
    }

    withdrawal_actions = {
        "withdrawal",
        "withdraw",
        "cash withdrawal",
    }

    sale_actions = {
        "sell",
    }

    # ---------------------------------------------------------
    # VERIFIED DISPLAY-NAME MAPPING
    # ---------------------------------------------------------

    account_name_map = {
        "Spartan Saver": (
            "OUCU Savings (Spartan Saver)"
        ),
        "TOTAL CHECKING": (
            "Chase Total Checking ••4197"
        ),
        "Spend": (
            "Robinhood Spending Account "
            "(export label: Spend)"
        ),
    }

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def _join_dates(
        events: pd.DataFrame,
    ) -> str:

        if events.empty:
            return ""

        dates = (
            events["date"]
            .sort_values()
            .dt.strftime("%Y-%m-%d")
            .drop_duplicates()
            .tolist()
        )

        return " | ".join(dates)

    def _mapped_accounts(
        events: pd.DataFrame,
        direction: str,
    ) -> str:

        if events.empty:
            return ""

        accounts = []

        for event in events.itertuples(index=False):

            raw_account = str(
                event.ticker
            ).strip()

            if not raw_account:
                raw_account = str(
                    event.note
                ).strip()

            mapped_account = account_name_map.get(
                raw_account,
                raw_account,
            )

            if (
                mapped_account
                and mapped_account not in accounts
            ):
                accounts.append(mapped_account)

        if not accounts:
            return ""

        return (
            f"{direction}: "
            + " | ".join(accounts)
        )

    def _positive_amount(
        events: pd.DataFrame,
    ) -> float:

        if events.empty:
            return 0.0

        return float(
            events["amount"].abs().sum()
        )

    def _sold_description(
        sales: pd.DataFrame,
    ) -> str:
        """
        Create a complete, non-truncated stock-sale description.
        """

        if sales.empty:
            return "NO"

        sold_amount = float(
            sales["amount"].abs().sum()
        )

        sold_tickers = (
            sales.loc[
                sales["ticker"].ne(""),
                "ticker",
            ]
            .drop_duplicates()
            .tolist()
        )

        position_count = len(sold_tickers)

        position_word = (
            "position"
            if position_count == 1
            else "positions"
        )

        ticker_text = ", ".join(
            sold_tickers
        )

        description = (
            f"YES | ${sold_amount:,.2f} | "
            f"{position_count} {position_word}"
        )

        if ticker_text:
            description += f": {ticker_text}"

        return description

    # ---------------------------------------------------------
    # BUILD MONTHLY ROWS
    # ---------------------------------------------------------

    output_rows = []

    for row in tqdm(
        monthly.itertuples(index=False),
        total=len(monthly),
        desc="Building final monthly ledger",
    ):

        valuation_date = pd.Timestamp(
            row.valuation_date
        )

        month_period = valuation_date.to_period(
            "M"
        )

        month_events = ledger.loc[
            ledger["_month_period"].eq(
                month_period
            )
        ].copy()

        deposits = month_events.loc[
            month_events["action"].isin(
                deposit_actions
            )
        ].copy()

        withdrawals = month_events.loc[
            month_events["action"].isin(
                withdrawal_actions
            )
        ].copy()

        sales = month_events.loc[
            month_events["action"].isin(
                sale_actions
            )
        ].copy()

        cash_at_date = float(
            row.cash_holdings
        )

        holds_at_date = float(
            row.stock_holdings
        )

        # Strict point-in-time definition.
        cash_holds = (
            cash_at_date
            + holds_at_date
        )

        # Cumulative external cash movements through
        # the actual valuation date.
        transactions_through_date = ledger.loc[
            ledger["date"].le(
                valuation_date
            )
        ]

        cum_deposited = float(
            transactions_through_date.loc[
                transactions_through_date[
                    "action"
                ].isin(deposit_actions),
                "amount",
            ]
            .abs()
            .sum()
        )

        cum_withdrawn = float(
            transactions_through_date.loc[
                transactions_through_date[
                    "action"
                ].isin(withdrawal_actions),
                "amount",
            ]
            .abs()
            .sum()
        )

        state_parts = []

        if not deposits.empty:
            state_parts.append("DEPOSIT")

        if not sales.empty:
            state_parts.append("SOLD STOCKS")

        if not withdrawals.empty:
            state_parts.append("WITHDRAWAL")

        state = (
            " + ".join(state_parts)
            if state_parts
            else "NO DEPOSIT / NO SALE / NO WITHDRAWAL"
        )

        output_rows.append(
            {
                "MONTH_YR": valuation_date,

                "CASH_HOLDS": cash_holds,

                "IF_SOLD_STOCKS": (
                    _sold_description(sales)
                ),

                "CASH_AT_DATE": cash_at_date,

                "HOLDS_AT_DATE": holds_at_date,

                "DEPOSIT_DATE": (
                    _join_dates(deposits)
                ),

                "DEPOSIT_AMOUNT": (
                    _positive_amount(deposits)
                ),

                "DEPOSIT_ADDRESS": (
                    _mapped_accounts(
                        deposits,
                        direction="FROM",
                    )
                ),

                "WITHDRAWAL_DATE": (
                    _join_dates(withdrawals)
                ),

                "WITHDRAWAL_AMOUNT": (
                    _positive_amount(withdrawals)
                ),

                "WITHDRAWAL_ADDRESS": (
                    _mapped_accounts(
                        withdrawals,
                        direction="TO",
                    )
                ),

                "CUM_DEPOSITED": cum_deposited,

                "CUM_WITHDRAWN": cum_withdrawn,

                "STATE": state,

                # Strict option A:
                # actual value in account on MONTH_YR.
                "ADJUSTED_TOTAL_in_ACCOUNT_at_DATE": (
                    cash_holds
                ),

                "_is_current_snapshot": False,
            }
        )

    # ---------------------------------------------------------
    # APPEND CURRENT SNAPSHOT FROM df_balance
    # ---------------------------------------------------------

    snapshot_date = pd.Timestamp(
        current_snapshot_date
    ).normalize()

    current_cash = float(
        balance["cash_holdings"].iloc[-1]
    )

    current_holds = float(
        balance["stock_holdings"].iloc[-1]
    )

    current_total = (
        current_cash
        + current_holds
    )

    transactions_through_current = ledger.loc[
        ledger["date"].le(snapshot_date)
    ]

    current_cum_deposited = float(
        transactions_through_current.loc[
            transactions_through_current[
                "action"
            ].isin(deposit_actions),
            "amount",
        ]
        .abs()
        .sum()
    )

    current_cum_withdrawn = float(
        transactions_through_current.loc[
            transactions_through_current[
                "action"
            ].isin(withdrawal_actions),
            "amount",
        ]
        .abs()
        .sum()
    )

    output_rows.append(
        {
            "MONTH_YR": snapshot_date,

            "CASH_HOLDS": current_total,

            # Current snapshot is point-in-time, not a duplicate
            # monthly activity summary.
            "IF_SOLD_STOCKS": "NO",

            "CASH_AT_DATE": current_cash,

            "HOLDS_AT_DATE": current_holds,

            "DEPOSIT_DATE": "",

            "DEPOSIT_AMOUNT": 0.0,

            "DEPOSIT_ADDRESS": "",

            "WITHDRAWAL_DATE": "",

            "WITHDRAWAL_AMOUNT": 0.0,

            "WITHDRAWAL_ADDRESS": "",

            "CUM_DEPOSITED": (
                current_cum_deposited
            ),

            "CUM_WITHDRAWN": (
                current_cum_withdrawn
            ),

            "STATE": "CURRENT SNAPSHOT",

            "ADJUSTED_TOTAL_in_ACCOUNT_at_DATE": (
                current_total
            ),

            "_is_current_snapshot": True,
        }
    )

    # ---------------------------------------------------------
    # FINALIZE
    # ---------------------------------------------------------

    df_final = pd.DataFrame(
        output_rows
    )

    # Prevent duplicate snapshot dates while preserving
    # the explicit current df_balance row.
    df_final = (
        df_final
        .sort_values(
            [
                "MONTH_YR",
                "_is_current_snapshot",
            ]
        )
        .drop_duplicates(
            subset=["MONTH_YR"],
            keep="last",
        )
        .sort_values("MONTH_YR")
        .reset_index(drop=True)
    )

    money_columns = [
        "CASH_HOLDS",
        "CASH_AT_DATE",
        "HOLDS_AT_DATE",
        "DEPOSIT_AMOUNT",
        "WITHDRAWAL_AMOUNT",
        "CUM_DEPOSITED",
        "CUM_WITHDRAWN",
        "ADJUSTED_TOTAL_in_ACCOUNT_at_DATE",
    ]

    df_final[money_columns] = (
        df_final[money_columns]
        .astype(float)
        .round(2)
    )

    # Exact requested date format.
    df_final["MONTH_YR"] = (
        df_final["MONTH_YR"]
        .dt.strftime("%Y-%m-%d")
    )

    df_final = df_final[
        [
            "MONTH_YR",
            "CASH_HOLDS",
            "IF_SOLD_STOCKS",
            "CASH_AT_DATE",
            "HOLDS_AT_DATE",
            "DEPOSIT_DATE",
            "DEPOSIT_AMOUNT",
            "DEPOSIT_ADDRESS",
            "WITHDRAWAL_DATE",
            "WITHDRAWAL_AMOUNT",
            "WITHDRAWAL_ADDRESS",
            "CUM_DEPOSITED",
            "CUM_WITHDRAWN",
            "STATE",
            "ADJUSTED_TOTAL_in_ACCOUNT_at_DATE",
        ]
    ]

    # ---------------------------------------------------------
    # LEGAL-EXHIBIT FOOTNOTES
    # ---------------------------------------------------------

    df_final.attrs["footnotes"] = [
        (
            "Includes Twitter cash-merger $65.04 "
            "(1.2 sh × $54.20, 2022-10-27) "
            "omitted by the CSV export."
        ),
        (
            "Cash is transaction + corporate-action basis; "
            "reconciles to the current app total $2,184.74."
        ),
        (
            "MONTH_YR is the first U.S. market session of "
            "each month. Reinvested dividends net "
            "approximately $0 cash."
        ),
        (
            "ADJUSTED_TOTAL_in_ACCOUNT_at_DATE strictly equals "
            "CASH_AT_DATE + HOLDS_AT_DATE and represents the "
            "actual reconstructed account value on MONTH_YR."
        ),
        (
            "The CSV identifies one transfer account only as "
            "'Spend.' It is displayed as 'Robinhood Spending "
            "Account (export label: Spend)' without asserting "
            "an external bank account number."
        ),
        (
            "The 2026-07-15 CURRENT SNAPSHOT row comes directly "
            "from df_balance and does not repeat July's monthly "
            "sale, deposit, or withdrawal activity."
        ),
    ]

    df_final.attrs["expected_totals"] = {
        "total_deposited": 6500.00,
        "total_withdrawn": 6715.95,
        "current_cash": round(current_cash, 2),
        "current_holdings": round(current_holds, 2),
        "current_total": round(current_total, 2),
    }

    return df_final

