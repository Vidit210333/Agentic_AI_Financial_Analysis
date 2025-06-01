
import numpy as np
import pandas as pd
from scipy import stats
import yfinance as yf
from crewai.tools import tool

@tool
def risk_assessment(ticker: str, benchmark: str = "SPY", period: str = "5y", risk_free_rate: float = 0.02):
    """
    Perform comprehensive risk assessment for a given stock with advanced metrics.
    
    Args:
        ticker (str): The stock ticker symbol.
        benchmark (str): Benchmark index for comparison (default: S&P 500).
        period (str): Time period for analysis.
        risk_free_rate (float): Annual risk-free rate (default: 2%).
    
    Returns:
        dict: Comprehensive risk assessment results.
    """
    try:
        # Get stock and benchmark data
        stock = yf.Ticker(ticker)
        benchmark_index = yf.Ticker(benchmark)
        
        # Fetch daily data
        stock_data = stock.history(period=period)
        benchmark_data = benchmark_index.history(period=period)
        
        # Ensure data alignment
        common_dates = stock_data.index.intersection(benchmark_data.index)
        stock_data = stock_data.loc[common_dates]
        benchmark_data = benchmark_data.loc[common_dates]
        
        # Calculate returns
        stock_returns = stock_data['Close'].pct_change().dropna()
        benchmark_returns = benchmark_data['Close'].pct_change().dropna()
        
        # Daily risk-free rate
        daily_rf = (1 + risk_free_rate) ** (1/252) - 1
        
        # Calculate beta using regression
        model = stats.linregress(benchmark_returns, stock_returns)
        beta = model.slope
        alpha = model.intercept * 252  # Annualized alpha
        r_squared = model.rvalue ** 2
        
        # Calculate volatility (annualized)
        volatility = stock_returns.std() * np.sqrt(252)
        
        # Calculate Sharpe ratio
        excess_returns = stock_returns - daily_rf
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        
        # Calculate Sortino ratio (downside risk only)
        negative_returns = excess_returns[excess_returns < 0]
        sortino_ratio = np.sqrt(252) * excess_returns.mean() / negative_returns.std() if len(negative_returns) > 0 else np.nan
        
        # Calculate Treynor ratio
        treynor_ratio = (stock_returns.mean() - daily_rf) * 252 / beta if beta != 0 else np.nan
        
        # Calculate various Value at Risk (VaR) metrics
        var_95 = np.percentile(stock_returns, 5)
        var_99 = np.percentile(stock_returns, 1)
        
        # Calculate Conditional VaR (CVaR) / Expected Shortfall
        cvar_95 = stock_returns[stock_returns <= var_95].mean()
        
        # Calculate Maximum Drawdown
        wealth_index = (1 + stock_returns).cumprod()
        previous_peaks = wealth_index.cummax()
        drawdowns = (wealth_index - previous_peaks) / previous_peaks
        max_drawdown = drawdowns.min()
        
        # Calculate downside deviation
        target_return = daily_rf  # Using risk-free rate as target
        downside_returns = stock_returns[stock_returns < target_return]
        downside_deviation = np.sqrt(((target_return - downside_returns) ** 2).sum() / len(stock_returns)) * np.sqrt(252)
        
        # Calculate Calmar ratio
        calmar_ratio = (stock_returns.mean() * 252) / abs(max_drawdown) if max_drawdown != 0 else np.nan
        
        # Calculate Kurtosis and Skewness
        kurtosis = stats.kurtosis(stock_returns)
        skewness = stats.skew(stock_returns)
        
        # Calculate Information Ratio
        tracking_error = (stock_returns - benchmark_returns).std() * np.sqrt(252)
        information_ratio = ((stock_returns.mean() - benchmark_returns.mean()) * 252) / tracking_error if tracking_error != 0 else np.nan
        
        # Calculate Omega Ratio
        threshold = daily_rf
        omega_ratio = stock_returns[stock_returns > threshold].sum() / abs(stock_returns[stock_returns < threshold].sum()) if abs(stock_returns[stock_returns < threshold].sum()) != 0 else np.nan
        
        # Calculate Ulcer Index (UI)
        drawdown_squared = drawdowns ** 2
        ulcer_index = np.sqrt(drawdown_squared.mean())
        
        # Calculate Tail Risk Metrics
        extreme_losses = stock_returns[stock_returns < var_95]
        tail_ratio = abs(np.percentile(stock_returns, 95)) / abs(np.percentile(stock_returns, 5)) if np.percentile(stock_returns, 5) != 0 else np.nan
        
        # Risk contribution to a hypothetical portfolio
        portfolio_variance = 0.5 ** 2 * volatility ** 2 + 0.5 ** 2 * benchmark_returns.std() ** 2 * 252 + 2 * 0.5 * 0.5 * beta * volatility * benchmark_returns.std() * 252
        risk_contribution = (0.5 * volatility ** 2 + 0.5 * beta * volatility * benchmark_returns.std() * 252) / portfolio_variance if portfolio_variance != 0 else np.nan
        
        # Prepare results in a structured format
        return {
            "ticker": ticker,
            "time_period": period,
            "benchmark": benchmark,
            
            # Core Risk Metrics
            "volatility": volatility,
            "beta": beta,
            "alpha": alpha,
            "r_squared": r_squared,
            
            # Downside Risk Metrics
            "value_at_risk_95": var_95,
            "value_at_risk_99": var_99,
            "conditional_var_95": cvar_95,
            "max_drawdown": max_drawdown,
            "downside_deviation": downside_deviation,
            "ulcer_index": ulcer_index,
            
            # Risk-Adjusted Performance Metrics
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "treynor_ratio": treynor_ratio,
            "calmar_ratio": calmar_ratio,
            "information_ratio": information_ratio,
            "omega_ratio": omega_ratio,
            
            # Statistical Properties
            "skewness": skewness,
            "kurtosis": kurtosis,
            "tail_ratio": tail_ratio,
            
            # Portfolio Context
            "risk_contribution": risk_contribution,
            
            # Risk Categorization (qualitative assessment)
            "risk_category": categorize_risk(beta, volatility, max_drawdown)
        }
    
    except Exception as e:
        print(f"Error in risk assessment: {str(e)}")
        return {
            "ticker": ticker,
            "error": str(e),
            "status": "failed"
        }

def categorize_risk(beta, volatility, max_drawdown):
    """
    Categorize risk profile based on multiple metrics.
    """
    risk_score = 0
    
    # Beta contribution
    if beta < 0.8:
        risk_score += 1  # Low beta
    elif 0.8 <= beta <= 1.2:
        risk_score += 2  # Medium beta
    else:
        risk_score += 3  # High beta
    
    # Volatility contribution
    if volatility < 0.15:
        risk_score += 1  # Low volatility
    elif 0.15 <= volatility <= 0.25:
        risk_score += 2  # Medium volatility
    else:
        risk_score += 3  # High volatility
    
    # Drawdown contribution
    if abs(max_drawdown) < 0.15:
        risk_score += 1  # Low drawdown
    elif 0.15 <= abs(max_drawdown) <= 0.3:
        risk_score += 2  # Medium drawdown
    else:
        risk_score += 3  # High drawdown
    
    # Categorize based on risk score
    if risk_score <= 4:
        return "Low Risk"
    elif risk_score <= 7:
        return "Medium Risk"
    else:
        return "High Risk"
