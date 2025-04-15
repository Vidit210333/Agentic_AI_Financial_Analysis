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
