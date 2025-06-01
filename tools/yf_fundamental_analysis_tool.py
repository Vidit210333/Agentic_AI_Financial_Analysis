
import yfinance as yf
from crewai.tools import tool

@tool
def yf_fundamental_analysis(ticker: str):
    """
    Perform comprehensive fundamental analysis on a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol.
    
    Returns:
        dict: Comprehensive fundamental analysis results.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Get financial data safely
    try:
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        
        # Calculate financial ratios if possible
        if not financials.empty and not balance_sheet.empty:
            try:
                current_ratio = balance_sheet.loc['Total Current Assets'].iloc[-1] / balance_sheet.loc['Total Current Liabilities'].iloc[-1]
            except:
                current_ratio = None
                
            try:
                debt_to_equity = balance_sheet.loc['Total Liabilities'].iloc[-1] / balance_sheet.loc['Total Stockholder Equity'].iloc[-1]
            except:
                debt_to_equity = None
                
            try:
                roe = financials.loc['Net Income'].iloc[-1] / balance_sheet.loc['Total Stockholder Equity'].iloc[-1]
            except:
                roe = None
                
            try:
                roa = financials.loc['Net Income'].iloc[-1] / balance_sheet.loc['Total Assets'].iloc[-1]
            except:
                roa = None
            
            # Calculate growth rates if we have at least 2 periods
            if len(financials.columns) >= 2:
                try:
                    revenue_growth = (financials.loc['Total Revenue'].iloc[-1] - financials.loc['Total Revenue'].iloc[-2]) / financials.loc['Total Revenue'].iloc[-2]
                except:
                    revenue_growth = None
                    
                try:
                    net_income_growth = (financials.loc['Net Income'].iloc[-1] - financials.loc['Net Income'].iloc[-2]) / financials.loc['Net Income'].iloc[-2]
                except:
                    net_income_growth = None
            else:
                revenue_growth = net_income_growth = None
            
            # Free Cash Flow calculation
            if not cash_flow.empty:
                try:
                    fcf = cash_flow.loc['Operating Cash Flow'].iloc[-1] - cash_flow.loc['Capital Expenditures'].iloc[-1]
                except:
                    fcf = None
            else:
                fcf = None
        else:
            current_ratio = debt_to_equity = roe = roa = revenue_growth = net_income_growth = fcf = None
    except:
        current_ratio = debt_to_equity = roe = roa = revenue_growth = net_income_growth = fcf = None
        financials = balance_sheet = cash_flow = None
    
    # Build result dict, safely getting values from info
    return {
        "ticker": ticker,
        "company_name": info.get('longName'),
        "sector": info.get('sector'),
        "industry": info.get('industry'),
        "market_cap": info.get('marketCap'),
        "pe_ratio": info.get('trailingPE'),
        "forward_pe": info.get('forwardPE'),
        "peg_ratio": info.get('pegRatio'),
        "price_to_book": info.get('priceToBook'),
        "dividend_yield": info.get('dividendYield'),
        "beta": info.get('beta'),
        "52_week_high": info.get('fiftyTwoWeekHigh'),
        "52_week_low": info.get('fiftyTwoWeekLow'),
        "current_ratio": current_ratio,
        "debt_to_equity": debt_to_equity,
        "return_on_equity": roe,
        "return_on_assets": roa,
        "revenue_growth": revenue_growth,
        "net_income_growth": net_income_growth,
        "free_cash_flow": fcf,
        "analyst_recommendation": info.get('recommendationKey'),
        "target_price": info.get('targetMeanPrice')
    }
