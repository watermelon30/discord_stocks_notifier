import pandas as pd
from data.fetcher import fetch_stock_data
from logic.evaluator import evaluate_group


def extract_ticker_df(raw_data: pd.DataFrame, ticker: str, num_tickers: int) -> pd.DataFrame | None:
    """
    Safely extract a single ticker's DataFrame from yfinance output.
    Handles both MultiIndex (multiple tickers) and flat (single ticker) structures.
    Returns None if the ticker data cannot be extracted or is invalid.
    """
    try:
        if isinstance(raw_data.columns, pd.MultiIndex):
            if ticker in raw_data.columns.get_level_values(0):
                return raw_data[ticker]
        elif num_tickers == 1:
            return raw_data
    except (KeyError, TypeError) as e:
        print(f"Warning: Could not extract data for {ticker}: {e}")

    return None


def get_all_tickers(config: dict) -> list[str]:
    """Extract a flat list of all tickers from ticker_categories."""
    categories = config.get("ticker_categories", {})
    all_tickers = []
    for tickers in categories.values():
        for t in tickers:
            if t not in all_tickers:
                all_tickers.append(t)
    return all_tickers


def get_ticker_category_map(config: dict) -> dict[str, str]:
    """Build a mapping of ticker -> category name."""
    categories = config.get("ticker_categories", {})
    ticker_to_category = {}
    for category, tickers in categories.items():
        for t in tickers:
            ticker_to_category[t] = category
    return ticker_to_category


def run_analysis(config: dict) -> dict[str, list[dict]]:
    """
    Fetch stock data and evaluate all rule groups against all tickers.
    Returns a dict mapping group description to a list of triggered ticker stats.
    Each stat dict includes a '_category' key for display grouping.
    """
    tickers = get_all_tickers(config)
    groups = config.get("groups", [])

    if not tickers or not groups:
        return {}

    ticker_to_category = get_ticker_category_map(config)
    raw_data = fetch_stock_data(tickers)
    results_by_group: dict[str, list[dict]] = {}

    for ticker in tickers:
        df = extract_ticker_df(raw_data, ticker, len(tickers))

        if df is None or df.empty or "Close" not in df.columns:
            continue

        close_series = df["Close"]

        for group in groups:
            triggered, group_title, stats = evaluate_group(close_series, group)
            if triggered:
                if group_title not in results_by_group:
                    results_by_group[group_title] = []
                stats["Ticker"] = ticker
                stats["_category"] = ticker_to_category.get(ticker, "Other")
                results_by_group[group_title].append(stats)

    return results_by_group
