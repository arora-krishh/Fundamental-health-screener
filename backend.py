import yfinance as yf
import pandas as pd
import numpy as np
SECTOR_TICKERS = {
    "Technology":  ["MSFT", "AAPL", "GOOGL", "NVDA", "META", "INTC", "AMD", "CRM", "ORCL", "ADBE"],
    "E-Commerce":  ["AMZN", "BABA", "SHOP", "ETSY", "EBAY", "JD", "PDD", "MELI"],
    "Automotive":  ["TSLA", "TM", "F", "GM", "HMC", "STLA", "RIVN", "NIO"],
    "Finance":     ["JPM", "BAC", "GS", "MS", "WFC", "C", "BLK", "AXP"],
    "Healthcare":  ["JNJ", "PFE", "UNH", "MRK", "ABBV", "LLY", "TMO", "ABT"],
    "Energy":      ["XOM", "CVX", "COP", "SLB", "EOG", "PXD", "OXY", "MPC"],
    "Logistics":   ["UPS", "FDX", "EXPD", "XPO", "CHRW", "JBHT", "SAIA", "ODFL"],
    "Consumer":    ["PG", "KO", "PEP", "WMT", "COST", "HD", "MCD", "NKE"],
}
PRESET_PROFILES = {
    "Conservative": {"P/E": 15, "D/E": 35, "ROE": 15, "Current Ratio": 35},
    "Growth":        {"P/E": 20, "D/E": 10, "ROE": 50, "Current Ratio": 20},
    "Value":         {"P/E": 50, "D/E": 20, "ROE": 20, "Current Ratio": 10},
    "Balanced":      {"P/E": 25, "D/E": 25, "ROE": 25, "Current Ratio": 25},
}
def fetch_stock_data(tickers: list) -> pd.DataFrame:
    screener_results = []

    for symbol in tickers:
        ticker = yf.Ticker(symbol)
        balance_sheet_df = ticker.quarterly_balance_sheet
        income_stmt_df   = ticker.quarterly_income_stmt

        try:
            # PE-ratio
            current_price    = ticker.info['currentPrice']
            EPS_avg_quaterly = income_stmt_df.loc['Diluted EPS'].head(4).sum()
            PEratio          = current_price / EPS_avg_quaterly

            # DE-ratio
            DEratio = (
                balance_sheet_df.loc['Total Debt'].iloc[0] /
                balance_sheet_df.loc['Stockholders Equity'].iloc[0]
            )

            # ROE
            return_on_equity = (
                income_stmt_df.loc['Net Income'].head(4).sum() /
                balance_sheet_df.loc['Stockholders Equity'].iloc[0]
            )

            # Current ratio
            current_assets      = balance_sheet_df.loc['Current Assets'].iloc[0]
            current_liabilities = balance_sheet_df.loc['Current Liabilities'].iloc[0]
            current_ratio       = current_assets / current_liabilities

            screener_results.append({
                "Ticker":        symbol,
                "Name":          ticker.info.get("shortName", symbol),
                "P/E ratio":     round(float(PEratio), 2),
                "D/E ratio":     round(float(DEratio), 2),
                "ROE":           round(float(return_on_equity), 4),
                "Current ratio": round(float(current_ratio), 2),
            })

        except Exception as e:
            print(f"Skipping {symbol} due to missing data: {e}")

    if not screener_results:
        return pd.DataFrame()

    final_df = pd.DataFrame(screener_results)
    final_df.set_index("Ticker", inplace=True)
    return final_df


def rank_and_score(df: pd.DataFrame, pe_w: float, de_w: float, roe_w: float, cr_w: float) -> pd.DataFrame:
    df = df.copy()

    # where lower is better
    df['P/E rank'] = df['P/E ratio'].rank(ascending=True)
    df['D/E rank'] = df['D/E ratio'].rank(ascending=True)

    # where higher is better
    df['ROE rank'] = df['ROE'].rank(ascending=False)
    df['Current ratio rank'] = df['Current ratio'].rank(ascending=False)

    total = pe_w + de_w + roe_w + cr_w
    df['Total score'] = (
        df['P/E rank'] * (pe_w  / total) +
        df['D/E rank'] * (de_w  / total) +
        df['ROE rank'] * (roe_w / total) +
        df['Current ratio rank'] * (cr_w  / total)
    ).round(2)

    return df.sort_values(by='Total score', ascending=True)


def run_screener(sector: str, pe_w: float, de_w: float, roe_w: float, cr_w: float) -> pd.DataFrame:
    tickers = SECTOR_TICKERS[sector]
    df      = fetch_stock_data(tickers)

    if df.empty:
        return pd.DataFrame()

    return rank_and_score(df, pe_w, de_w, roe_w, cr_w)
