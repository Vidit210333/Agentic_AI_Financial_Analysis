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
            "competitors": [{
                "ticker": str,
                "name": str,
                "market_cap": float,
                "pe_ratio": float,
                "revenue_growth": float,
                "profit_margins": float,
                "beta": float
            }]
        }
    """
    try:
        # Get base stock info
        stock = yf.Ticker(ticker)
        info = stock.info
        sector = info.get('sector')
        industry = info.get('industry')
        
        if not sector or not industry:
            raise ValueError(f"Could not determine sector/industry for {ticker}")

        # Method 1: Use Yahoo Finance's recommendation API
        competitors = set()
        url = f"https://query2.finance.yahoo.com/v6/finance/recommendationsbysymbol/{ticker}"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            data = response.json()
            for rec in data.get('finance', {}).get('result', []):
                competitors.update(s['symbol'] for s in rec.get('recommendedSymbols', []))

        # Method 2: Fallback to sector ETF holdings if needed
        if len(competitors) < num_competitors:
            sector_etf = {
                'Technology': 'XLK',
                'Financial Services': 'XLF',
                'Healthcare': 'XLV',
                'Consumer Cyclical': 'XLY',
                'Communication Services': 'XLC'
            }.get(sector)
            
            if sector_etf:
                etf = yf.Ticker(sector_etf)
                holdings = etf.info.get('holdings', {})
                competitors.update(holdings.keys())

        # Process competitors
        competitor_data = []
        for comp in list(competitors):
            if comp == ticker:
                continue
                
            try:
                comp_stock = yf.Ticker(comp)
                comp_info = comp_stock.info
                
                # Only include companies in the same industry
                if comp_info.get('industry') == industry:
                    competitor_data.append({
                        "ticker": comp,
                        "name": comp_info.get('longName', comp),
                        "market_cap": comp_info.get('marketCap'),
                        "pe_ratio": comp_info.get('trailingPE'),
                        "revenue_growth": comp_info.get('revenueGrowth'),
                        "profit_margins": comp_info.get('profitMargins'),
                        "beta": comp_info.get('beta')
                    })
                    
                    if len(competitor_data) >= num_competitors:
                        break
            except:
                continue

        return {
            "status": "success",
            "main_stock": {
                "ticker": ticker,
                "name": info.get('longName'),
                "sector": sector,
                "industry": industry
            },
            "competitors": sorted(
                competitor_data,
                key=lambda x: x.get('market_cap', 0),
                reverse=True
            )[:num_competitors]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to analyze competitors: {str(e)}",
            "ticker": ticker
        }