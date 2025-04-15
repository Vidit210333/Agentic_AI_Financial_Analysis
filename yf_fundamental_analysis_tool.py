# import yfinance as yf
# from crewai.tools import BaseTool

# class FundamentalAnalysisTool(BaseTool):
#     name : str = "Fundamental Analysis Tool"
#     description : str = "Performs comprehensive fundamental analysis including financial ratios, valuation metrics, and growth indicators."
    
#     def _run(self, ticker: str) -> dict:
#         """
#         Perform comprehensive fundamental analysis on a given stock ticker.
        
#         Args:
#             ticker (str): The stock ticker symbol to analyze.
            
#         Returns:
#             dict: Contains:
#                 - Basic company information (name, sector, industry)
#                 - Valuation metrics (P/E, P/B, PEG, etc.)
#                 - Financial health ratios (current ratio, debt-to-equity)
#                 - Profitability metrics (ROE, ROA)
#                 - Growth indicators (revenue growth, net income growth)
#                 - Cash flow analysis (free cash flow)
#                 - Market data (52-week range, beta)
#                 - Analyst estimates (recommendation, target price)
#         """
#         stock = yf.Ticker(ticker)
#         info = stock.info
        
#         # Get financial statements
#         financials = stock.financials
#         balance_sheet = stock.balance_sheet
#         cash_flow = stock.cashflow
        
#         # Calculate financial ratios with error handling
#         ratios = self._calculate_financial_ratios(financials, balance_sheet, cash_flow)
        
#         return {
#             "ticker": ticker,
#             "company_name": info.get('longName'),
#             "sector": info.get('sector'),
#             "industry": info.get('industry'),
#             "market_cap": info.get('marketCap'),
#             "valuation_metrics": {
#                 "pe_ratio": info.get('trailingPE'),
#                 "forward_pe": info.get('forwardPE'),
#                 "peg_ratio": info.get('pegRatio'),
#                 "price_to_book": info.get('priceToBook'),
#                 "dividend_yield": info.get('dividendYield')
#             },
#             "financial_health": {
#                 "current_ratio": ratios.get('current_ratio'),
#                 "debt_to_equity": ratios.get('debt_to_equity')
#             },
#             "profitability": {
#                 "return_on_equity": ratios.get('roe'),
#                 "return_on_assets": ratios.get('roa')
#             },
#             "growth_indicators": {
#                 "revenue_growth": ratios.get('revenue_growth'),
#                 "net_income_growth": ratios.get('net_income_growth')
#             },
#             "cash_flow": {
#                 "free_cash_flow": ratios.get('fcf')
#             },
#             "market_data": {
#                 "beta": info.get('beta'),
#                 "52_week_high": info.get('fiftyTwoWeekHigh'),
#                 "52_week_low": info.get('fiftyTwoWeekLow')
#             },
#             "analyst_estimates": {
#                 "recommendation": info.get('recommendationKey'),
#                 "target_price": info.get('targetMeanPrice')
#             }
#         }

#     def _calculate_financial_ratios(self, financials, balance_sheet, cash_flow) -> dict:
#         """Calculate key financial ratios from statements."""
#         try:
#             current_ratio = (balance_sheet.loc['Total Current Assets'].iloc[-1] / 
#                            balance_sheet.loc['Total Current Liabilities'].iloc[-1])
            
#             debt_to_equity = (balance_sheet.loc['Total Liabilities'].iloc[-1] / 
#                             balance_sheet.loc['Total Stockholder Equity'].iloc[-1])
            
#             roe = (financials.loc['Net Income'].iloc[-1] / 
#                   balance_sheet.loc['Total Stockholder Equity'].iloc[-1])
            
#             roa = (financials.loc['Net Income'].iloc[-1] / 
#                   balance_sheet.loc['Total Assets'].iloc[-1])
            
#             # Calculate growth rates if we have at least 2 years of data
#             if len(financials.loc['Total Revenue']) >= 2:
#                 revenue_growth = ((financials.loc['Total Revenue'].iloc[-1] - 
#                                  financials.loc['Total Revenue'].iloc[-2]) / 
#                                 financials.loc['Total Revenue'].iloc[-2])
                
#                 net_income_growth = ((financials.loc['Net Income'].iloc[-1] - 
#                                     financials.loc['Net Income'].iloc[-2]) / 
#                                    financials.loc['Net Income'].iloc[-2])
#             else:
#                 revenue_growth = net_income_growth = None
            
#             # Free Cash Flow calculation
#             fcf = (cash_flow.loc['Operating Cash Flow'].iloc[-1] - 
#                   cash_flow.loc['Capital Expenditures'].iloc[-1])
            
#             return {
#                 'current_ratio': current_ratio,
#                 'debt_to_equity': debt_to_equity,
#                 'roe': roe,
#                 'roa': roa,
#                 'revenue_growth': revenue_growth,
#                 'net_income_growth': net_income_growth,
#                 'fcf': fcf
#             }
            
#         except Exception as e:
#             # Return None for all ratios if calculation fails
#             return {key: None for key in [
#                 'current_ratio', 'debt_to_equity', 'roe', 'roa',
#                 'revenue_growth', 'net_income_growth', 'fcf'
#             ]}

# # Create an instance of the tool
# fundamental_analysis_tool = FundamentalAnalysisTool()

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