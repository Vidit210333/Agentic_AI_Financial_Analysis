

import yfinance as yf
from crewai.tools import tool
import requests
from typing import Dict, List

@tool
def competitor_analysis(ticker: str, num_competitors: int = 5) -> Dict:
    """
    Identifies and analyzes top competitors for a given stock.
    
    Args:
        ticker (str): Stock symbol to analyze (e.g., 'AAPL')
        num_competitors (int): Number of competitors to return (default: 5)
        
    Returns:
        dict: {
            "main_stock": {
                "ticker": str,
                "name": str,
                "sector": str,
                "industry": str
            },
            "competitors": [ ... ]
        }
    """
    try:
        # Get base stock info
        stock = yf.Ticker(ticker)
        info = stock.info
        sector = info.get('sector')
        industry = info.get('industry')
        name = info.get('shortName') or info.get('longName', ticker)

        if not sector or not industry:
            raise ValueError(f"Could not determine sector/industry for {ticker}")

        # Try Method 1: Use Yahoo Finance recommendation API
        competitors = set()
        url = f"https://query2.finance.yahoo.com/v6/finance/recommendationsbysymbol/{ticker}"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

        if response.status_code == 200:
            data = response.json()
            for rec in data.get('finance', {}).get('result', []):
                competitors.update(s['symbol'] for s in rec.get('recommendedSymbols', []))

        # Fallback: Use predefined sector ETFs to find similar companies
        if len(competitors) < num_competitors:
            sector_etfs = {
                "Technology": "XLK",
                "Healthcare": "XLV",
                "Financial Services": "XLF",
                "Consumer Cyclical": "XLY",
                "Energy": "XLE",
                "Industrials": "XLI",
                "Utilities": "XLU",
                "Materials": "XLB",
                "Real Estate": "XLRE",
                "Communication Services": "XLC"
            }

            etf_symbol = sector_etfs.get(sector)
            if etf_symbol:
                etf = yf.Ticker(etf_symbol)
                holdings = etf.info.get('holdings', [])
                # Yahoo Finance may not always expose ETF holdings via API
                etf_holdings = etf.history(period="1d").columns.tolist()
                for sym in etf_holdings:
                    if sym != ticker:
                        competitors.add(sym)

        # Limit number of competitors
        competitors = list(competitors - {ticker})[:num_competitors]

        competitor_data = []
        for comp in competitors:
            try:
                comp_info = yf.Ticker(comp).info
                competitor_data.append({
                    "ticker": comp,
                    "name": comp_info.get('shortName', ''),
                    "market_cap": comp_info.get('marketCap', 0),
                    "pe_ratio": comp_info.get('trailingPE', 0),
                    "revenue_growth": comp_info.get('revenueGrowth', 0),
                    "profit_margins": comp_info.get('profitMargins', 0),
                    "beta": comp_info.get('beta', 0)
                })
            except Exception:
                continue  # Skip if any issue occurs

        return {
            "main_stock": {
                "ticker": ticker,
                "name": name,
                "sector": sector,
                "industry": industry
            },
            "competitors": competitor_data
        }

    except Exception as e:
        return {"error": str(e)}
