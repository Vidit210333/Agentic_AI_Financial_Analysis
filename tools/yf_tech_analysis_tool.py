
import yfinance as yf
import pandas as pd
import numpy as np
from crewai.tools import tool
from ta import add_all_ta_features
from ta.utils import dropna
from scipy.signal import find_peaks

@tool
def yf_tech_analysis(ticker: str):
    
    """
    Perform advanced technical analysis on a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol.
    
    Returns:
        dict: Advanced technical analysis results.
    """
    period  = "2y"
    try:
        # Get stock data with a longer interval to ensure we have enough data
        stock = yf.Ticker(ticker)
        # Use "1d" interval to get daily data which is more reliable
        history = stock.history(period=period, interval="1d")
        
        # Check if we have data
        if len(history) < 30:
            return {"error": f"Insufficient data points ({len(history)}) for ticker {ticker}"}
        
        # Process the data without dropping NA values immediately
        # Fill NaN values in OHLC data 
        history = history.ffill().bfill()  # Forward fill then backward fill
        
        # Ensure we have all required columns
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in required_columns:
            if col not in history.columns or history[col].isnull().all():
                return {"error": f"Missing required column {col} for {ticker}"}
        
        # Save original Close prices
        close_prices = history['Close'].values
        
        # Add all technical analysis features with explicit handling for NaN values
        df = history.copy()
        df = add_all_ta_features(
            df, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True
        )
        
        # Manually calculate SMA values if they're not in the dataframe
        if 'trend_sma_50' not in df.columns:
            print("Manually calculating SMA-50")
            df['trend_sma_50'] = df['Close'].rolling(window=50).mean()
        
        if 'trend_sma_200' not in df.columns:
            print("Manually calculating SMA-200")
            df['trend_sma_200'] = df['Close'].rolling(window=200).mean()
        
        # Calculate additional custom indicators
        window_size = min(20, max(5, len(df) // 10))  # Adaptive window size
        df['volatility'] = df['Close'].pct_change().rolling(window=window_size).std().fillna(0) * np.sqrt(252)
        df['momentum'] = (df['Close'] - df['Close'].shift(window_size)).fillna(0)
        
        # Calculate RSI manually if not present
        if 'momentum_rsi' not in df.columns:
            print("Manually calculating RSI")
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).fillna(0)
            loss = -delta.where(delta < 0, 0).fillna(0)
            
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            
            rs = avg_gain / avg_loss.replace(0, 0.001)  # Avoid division by zero
            df['momentum_rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD manually if not present
        if 'trend_macd_diff' not in df.columns:
            print("Manually calculating MACD")
            ema12 = df['Close'].ewm(span=12, adjust=False).mean()
            ema26 = df['Close'].ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            df['trend_macd_diff'] = macd_line - signal_line
        
        # Calculate Bollinger Bands manually if not present
        if 'volatility_bbhi' not in df.columns or 'volatility_bbli' not in df.columns:
            print("Manually calculating Bollinger Bands")
            sma20 = df['Close'].rolling(window=20).mean()
            std20 = df['Close'].rolling(window=20).std()
            
            upper_band = sma20 + (std20 * 2)
            lower_band = sma20 - (std20 * 2)
            
            # Binary indicators for price touching bands
            df['volatility_bbhi'] = (df['Close'] >= upper_band).astype(float)
            df['volatility_bbli'] = (df['Close'] <= lower_band).astype(float)
        
        # Calculate ATR manually if not present
        if 'volatility_atr' not in df.columns:
            print("Manually calculating ATR")
            high_low = df['High'] - df['Low']
            high_close = (df['High'] - df['Close'].shift()).abs()
            low_close = (df['Low'] - df['Close'].shift()).abs()
            
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            df['volatility_atr'] = true_range.rolling(14).mean()
        
        # Identify potential support and resistance levels
        if len(close_prices) >= 30:
            distance = max(5, len(close_prices) // 20)  # Adaptive distance parameter
            peaks, _ = find_peaks(close_prices, distance=distance)
            troughs, _ = find_peaks(-close_prices, distance=distance)
            
            support_levels = close_prices[troughs][-3:] if len(troughs) > 0 else []
            resistance_levels = close_prices[peaks][-3:] if len(peaks) > 0 else []
        else:
            support_levels = []
            resistance_levels = []
        
        patterns = _identify_chart_patterns(df) if len(df) >= 30 else []
        
        # Fill NaN values in calculated indicators
        for col in ['trend_sma_50', 'trend_sma_200', 'momentum_rsi', 'trend_macd_diff', 
                    'volatility_bbhi', 'volatility_bbli', 'volatility_atr']:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # Prepare result dictionary
        result = {
            "ticker": ticker,
            "current_price": float(df['Close'].iloc[-1]),
            "sma_50": float(df['trend_sma_50'].iloc[-1]) if not pd.isna(df['trend_sma_50'].iloc[-1]) else None,
            "sma_200": float(df['trend_sma_200'].iloc[-1]) if not pd.isna(df['trend_sma_200'].iloc[-1]) else None,
            "rsi": float(df['momentum_rsi'].iloc[-1]) if not pd.isna(df['momentum_rsi'].iloc[-1]) else None,
            "macd": float(df['trend_macd_diff'].iloc[-1]) if not pd.isna(df['trend_macd_diff'].iloc[-1]) else None,
            "bollinger_hband": float(df['volatility_bbhi'].iloc[-1]) if not pd.isna(df['volatility_bbhi'].iloc[-1]) else None,
            "bollinger_lband": float(df['volatility_bbli'].iloc[-1]) if not pd.isna(df['volatility_bbli'].iloc[-1]) else None,
            "atr": float(df['volatility_atr'].iloc[-1]) if not pd.isna(df['volatility_atr'].iloc[-1]) else None,
            "volatility": float(df['volatility'].iloc[-1]) if not pd.isna(df['volatility'].iloc[-1]) else None,
            "momentum": float(df['momentum'].iloc[-1]) if not pd.isna(df['momentum'].iloc[-1]) else None,
            "support_levels": [float(x) for x in support_levels] if len(support_levels) > 0 else [],
            "resistance_levels": [float(x) for x in resistance_levels] if len(resistance_levels) > 0 else [],
            "identified_patterns": patterns,
            "data_points": len(df)
        }
        
        # Print some debugging info
        print(f"Analysis completed successfully for {ticker}")
        
        return result
        
    except Exception as e:
        import traceback
        print(f"Error in technical analysis: {str(e)}")
        print(traceback.format_exc())
        # Provide more descriptive error message
        return {
            "error": f"Error analyzing {ticker}: {str(e)}",
            "ticker": ticker
        }

def _identify_chart_patterns(df):
    patterns = []
    
    if len(df) < 30:
        return patterns
        
    try:
        close = df['Close'].values
        
        if _is_head_and_shoulders(close):
            patterns.append("Head and Shoulders")
        
        if _is_double_top(close):
            patterns.append("Double Top")
        
        if _is_double_bottom(close):
            patterns.append("Double Bottom")
    except Exception as e:
        print(f"Error identifying patterns: {str(e)}")
        
    return patterns

def _is_head_and_shoulders(close):
    if len(close) < 60:
        return False
        
    try:
        peaks, _ = find_peaks(close, distance=max(5, len(close) // 20))
        if len(peaks) >= 3:
            left_shoulder, head, right_shoulder = peaks[-3], peaks[-2], peaks[-1]
            if close[head] > close[left_shoulder] and close[head] > close[right_shoulder]:
                return True
    except Exception:
        pass
    return False

def _is_double_top(close):
    if len(close) < 40:
        return False
        
    try:
        peaks, _ = find_peaks(close, distance=max(5, len(close) // 20))
        if len(peaks) >= 2:
            if abs(close[peaks[-1]] - close[peaks[-2]]) / close[peaks[-2]] < 0.03:
                return True
    except Exception:
        pass
    return False

def _is_double_bottom(close):
    if len(close) < 40:
        return False
        
    try:
        troughs, _ = find_peaks(-close, distance=max(5, len(close) // 20))
        if len(troughs) >= 2:
            if abs(close[troughs[-1]] - close[troughs[-2]]) / close[troughs[-2]] < 0.03:
                return True
    except Exception:
        pass
    return False
