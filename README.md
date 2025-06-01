# Financial Analysis: Multi-Agent Open Source LLM

An advanced stock analysis tool powered by AI agents that provides comprehensive financial analysis using open-source language models. This application combines technical analysis, fundamental analysis, and sentiment analysis to deliver detailed insights for stock market investments.

## Problem Statement 

In the complex and volatile world of financial markets, making informed investment decisions requires analyzing vast and diverse information: stock trends, company fundamentals, news sentiment, and industry comparisons. Traditional approaches often rely on fragmented tools and manual effort, making it difficult to generate a holistic view.

Agentic AI Financial Analysis solves this by leveraging multiple autonomous AI agents to collaboratively analyze financial data, generate insights, assess risks, and recommend investment strategies — all in a structured and automated pipeline.

## Agent Interactions 

This system is built using an agentic architecture where each agent is responsible for a specific analytical task. Agents interact and pass information to form a comprehensive financial overview.

Stock Data Agent: Collects real-time data for selected stocks.
Technical Analysis Agent: Analyzes patterns, trends, and indicators (e.g., moving averages, RSI).
Fundamental Analysis Agent: Fetches and interprets company financials (P/E ratio, revenue, etc.).
Sentiment Analysis Agent: Scrapes and evaluates market sentiment from news or social media.
Risk Assessment Agent: Evaluates investment risks based on volatility and financial indicators.
Competitor Analysis Agent: Identifies and compares peer companies.
Strategy Recommendation Agent: Compiles insights from all agents to recommend an investment strategy.

All agents are orchestrated using a central CrewAI-based management system (crew.py), which controls task flow and knowledge sharing between agents.

## Features

- Real-time stock data analysis
- Technical analysis with chart pattern recognition
- Fundamental analysis of company financials
- Market sentiment analysis
- Risk assessment
- Competitor analysis
- Investment strategy recommendations
- Interactive charts and visualizations

## StreamLit Application 

1. Enter a stock symbol (e.g., AAPL for Apple Inc.) in the input field.
2. Click "Analyze Stock" to generate a comprehensive analysis report.

The application will display:
- Technical analysis insights
- Chart patterns
- Fundamental analysis
- Market sentiment
- Risk assessment
- Competitor analysis
- Investment strategy recommendations

## Dependencies

Python 3.10+

- CrewAI – Agentic AI Framework
- LangChain / LLMs – For reasoning and text generation (We have currently used Gemini 2.0 - flash)
- Pandas / NumPy – Data processing
- Matplotlib / Plotly – Visualizations
- yfinance – Real-time stock data and other key financial values of a stock
- BeautifulSoup / requests – Web scraping for news articles from finnewz
- HuggingFace – Sentiment Analysis
- Streamlit (optional) – Interactive UI (can be added)


## Setup and run instructions 
### 1. Clone the Repository

```bash
git clone https://github.com/Vidit210333/Agentic_AI_Financial_Analysis.git
cd Agentic_AI_Financial_Analysis

