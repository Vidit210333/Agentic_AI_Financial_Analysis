# import streamlit as st
# import yfinance as yf
# import plotly.graph_objs as go
# from crew import run_analysis
# import json

# def main():
#     st.set_page_config(layout="wide")
#     st.title("AI-Powered Advanced Stock Analysis")

#     # User input
#     stock_symbol = st.text_input("Enter stock symbol (e.g., AAPL):", "AAPL")
    
#     if st.button("Analyze Stock"):
#         # Run CrewAI analysis
#         with st.spinner("Performing comprehensive stock analysis..."):
#             # result = run_analysis(stock_symbol)
#             crew_result = run_analysis(stock_symbol)
#             for role, analysis in crew_result["individual_analyses"].items():
#                 print(f"\n\n=== {role}'s Analysis ===")
#                 print(analysis)

#         # Access the final result
#             # print("\n\n=== Final Integrated Analysis ===")
#             # print(crew_result["final_result"])
#                 # Solution 1: Direct string conversion (most reliable)
#             try:
#                     analysis = json.loads(str(crew_result))
#             except json.JSONDecodeError:
#                     # If not valid JSON, wrap it
#                     analysis = {"analysis": str(crew_result)}
                
#                 # Display results
#             st.header("AI Analysis Report")
#             st.json(analysis)  # Prr JSON displayo

#         # Display analysis result
#         st.header("AI Analysis Report")
#         # # Parse the result
#         # analysis = json.loads(result.result) 
        
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.subheader("Technical Analysis")
#             st.write(analysis.get('technical_analysis', 'No technical analysis available'))
            
#             st.subheader("Chart Patterns")
#             st.write(analysis.get('chart_patterns', 'No chart patterns identified'))
        
#         with col2:
#             st.subheader("Fundamental Analysis")
#             st.write(analysis.get('fundamental_analysis', 'No fundamental analysis available'))
            
#             st.subheader("Sentiment Analysis")
#             st.write(analysis.get('sentiment_analysis', 'No sentiment analysis available'))
        
#         st.subheader("Risk Assessment")
#         st.write(analysis.get('risk_assessment', 'No risk assessment available'))
        
#         st.subheader("Competitor Analysis")
#         st.write(analysis.get('competitor_analysis', 'No competitor analysis available'))
        
#         st.subheader("Investment Strategy")
#         st.write(analysis.get('investment_strategy', 'No investment strategy available'))
        
#         # Fetch stock data for chart
#         stock = yf.Ticker(stock_symbol)
#         hist = stock.history(period="1y")
        
#         # Create interactive chart
#         fig = go.Figure()
#         fig.add_trace(go.Candlestick(x=hist.index,
#                                      open=hist['Open'],
#                                      high=hist['High'],
#                                      low=hist['Low'],
#                                      close=hist['Close'],
#                                      name='Price'))
        
#         # Add volume bars
#         fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', yaxis='y2'))
        
#         # Add moving averages
#         fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=50).mean(), name='50-day MA'))
#         fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=200).mean(), name='200-day MA'))
        
#         fig.update_layout(
#             title=f"{stock_symbol} Stock Analysis",
#             yaxis_title='Price',
#             yaxis2=dict(title='Volume', overlaying='y', side='right'),
#             xaxis_rangeslider_visible=False
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
        
#         # Display key statistics
#         st.subheader("Key Statistics")
#         info = stock.info
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}")
#             st.metric("P/E Ratio", round(info.get('trailingPE', 0), 2))
#         with col2:
#             st.metric("52 Week High", f"${info.get('fiftyTwoWeekHigh', 0):,.2f}")
#             st.metric("52 Week Low", f"${info.get('fiftyTwoWeekLow', 0):,.2f}")
#         with col3:
#             st.metric("Dividend Yield", f"{info.get('dividendYield', 0):.2%}")
#             st.metric("Beta", round(info.get('beta', 0), 2))

# if __name__ == "__main__":
#     main()

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from crew import run_analysis
import json
from datetime import datetime

def display_analysis_card(title, content, is_json=False):
    """Display an analysis block with consistent styling"""
    with st.container():
        st.subheader(title)
        if is_json:
            st.json(content)
        else:
            st.write(content)
        st.divider()

def display_stock_chart(ticker):
    """Show interactive price chart with technical indicators"""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist['Open'],
        high=hist['High'],
        low=hist['Low'],
        close=hist['Close'],
        name='Price'
    ))
    
    # Add technical indicators
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist['Close'].rolling(50).mean(),
        name='50-day MA',
        line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist['Close'].rolling(200).mean(),
        name='200-day MA',
        line=dict(color='orange', width=2)
    ))
    
    fig.update_layout(
        title=f"{ticker} Price Chart with Moving Averages",
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=False,
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(layout="wide", page_title="Stock Analysis Dashboard")
    st.title("📊 Stock Analysis Dashboard")
    
    # User input
    stock_symbol = st.text_input("Enter stock symbol (e.g., AAPL):", "AAPL").upper()
    
    if st.button("Run Analysis"):
        with st.spinner(f"🧠 Analyzing {stock_symbol} - This may take a few minutes..."):
            try:
                # Display basic stock info first
                stock = yf.Ticker(stock_symbol)
                info = stock.info
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"Company Overview: {info.get('longName', stock_symbol)}")
                    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                    st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                    st.write(f"**Current Price:** ${info.get('currentPrice', 'N/A'):,.2f}")
                
                with col2:
                    st.subheader("Key Metrics")
                    st.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.2f}B")
                    st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
                    st.metric("52 Week Range", 
                            f"${info.get('fiftyTwoWeekLow', 'N/A'):,.2f} - ${info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}")
                
                # Show price chart
                display_stock_chart(stock_symbol)
                
                # Run analysis and display individual components
                st.divider()
                st.header("Detailed Analysis Components")
                
                analysis_results = run_analysis(stock_symbol)
                # analysis_results = {}
                # Display each analysis component in its own block
                for role, analysis in analysis_results["individual_analyses"].items():
                    if isinstance(analysis, dict):
                        display_analysis_card(
                            f"🔍 {role}",
                            analysis,
                            is_json=True
                        )
                    else:
                        display_analysis_card(
                            f"🔍 {role}",
                            str(analysis)
                        )
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.exception(e)

if __name__ == "__main__":
    main()