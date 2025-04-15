# import yfinance as yf
# from textblob import TextBlob
# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# from crewai.tools import BaseTool
# from typing import List, Dict
# import json

# class ReliableSentimentAnalysisTool(BaseTool):
#     name: str = "Stock News Sentiment Analysis Tool"
#     description: str = "Analyzes sentiment from reliable free sources (Yahoo Finance, Finviz, Benzinga)"
    
#     def _run(self, ticker: str) -> dict:
#         """
#         Get sentiment analysis from reliable free news sources
        
#         Args:
#             ticker (str): Stock ticker symbol (e.g., 'AAPL')
            
#         Returns:
#             dict: Sentiment analysis results
#         """
#         # Get news from reliable sources
#         news_articles = []
#         news_articles.extend(self._get_yfinance_news(ticker))  # First 10 articles
#         news_articles.extend(self._get_finviz_news(ticker))     # First 10 articles
    
#         # Analyze sentiment
#         return self._analyze_sentiment(news_articles)
    
#     def _get_yfinance_news(self, ticker: str) -> List[Dict]:
#         """Get news from Yahoo Finance using yfinance"""
#         try:
#             stock = yf.Ticker(ticker)
#             news = stock.news
            
#             articles = []
#             for article in news[:30]:  # Get the 5 most recent articles
#                 try:
#                     article_data = {
#                         'title': article['content']['title'],
#                         'source': 'Yahoo Finance'
#                     }
#                     articles.append(article_data)
#                 except KeyError as e:
#                     print(f"Malformed article data, missing key: {str(e)}")
#                     continue
            
#             return articles
#         except Exception as e:
#             print(f"Yahoo Finance error: {str(e)}")
#             return []
    
#     def _get_finviz_news(self, ticker: str) -> List[Dict]:
#         """Get news from Finviz"""
#         try:
#             headers = {
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#             }
#             url = f"https://finviz.com/quote.ashx?t={ticker}"
#             response = requests.get(url, headers=headers, timeout=10)
#             response.raise_for_status()
            
#             soup = BeautifulSoup(response.text, 'html.parser')
#             news_table = soup.find(id='news-table')
#             if not news_table:
#                 return []
            
#             articles = []
#             for row in news_table.find_all('tr'):
#                 title = row.a.text if row.a else 'No title'
#                 date_data = row.td.text.split(' ') if row.td else []
#                 date = date_data[0] if len(date_data) > 1 else datetime.now().strftime("%Y-%m-%d")
                
#                 articles.append({
#                     'title': title,
#                     'source': 'Finviz',
#                     'date': date,
#                     'link': row.a['href'] if row.a and 'href' in row.a.attrs else '',
#                     'content': ''
#                 })
#                 if len(articles) >= 30 :
#                     break
#             return articles
#         except Exception as e:
#             print(f"Finviz error: {str(e)}")
#             return []
    
#     def _analyze_sentiment(self, articles: List[Dict]) -> Dict:
#         """Analyze sentiment from collected articles"""
#         if not articles:
#             return {
#                 'average_sentiment': 0,
#                 'positive_articles': 0,
#                 'neutral_articles': 0,
#                 'negative_articles': 0,
#                 'total_articles': 0,
#                 'sources': [],
#                 'sentiment_interpretation': 'No Data'
#             }
        
#         sentiments = []
#         sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
#         sources = set()
        
#         for article in articles:
#             text = article['title']  # Use title for sentiment analysis
#             blob = TextBlob(text)
#             sentiment = blob.sentiment.polarity
#             sentiments.append(sentiment)
            
#             # Categorize sentiment
#             if sentiment > 0.2:
#                 sentiment_counts['positive'] += 1
#             elif sentiment < -0.2:
#                 sentiment_counts['negative'] += 1
#             else:
#                 sentiment_counts['neutral'] += 1
            
#             sources.add(article.get('source', 'Unknown'))
        
#         avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
#         return {
#             'average_sentiment': round(avg_sentiment, 3),
#             'positive_articles': sentiment_counts['positive'],
#             'neutral_articles': sentiment_counts['neutral'],
#             'negative_articles': sentiment_counts['negative'],
#             'total_articles': len(articles),
#             'sources': list(sources),
#             'sentiment_interpretation': self._interpret_sentiment(avg_sentiment)
#         }
    
#     def _interpret_sentiment(self, score: float) -> str:
#         """Convert sentiment score to human-readable interpretation"""
#         if score > 0.3:
#             return "Strongly Positive"
#         elif score > 0.1:
#             return "Positive"
#         elif score < -0.3:
#             return "Strongly Negative"
#         elif score < -0.1:
#             return "Negative"
#         else:
#             return "Neutral"

# # Example usage

# sentiment_analysis_tool = ReliableSentimentAnalysisTool()

import yfinance as yf
from crewai.tools import tool
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup

@tool
def sentiment_analysis(ticker: str):
    """
    Perform sentiment analysis on recent news articles about the given stock.
    
    Args:
        ticker (str): The stock ticker symbol.
    
    Returns:
        dict: Sentiment analysis results.
    """
    news_articles = []
    news_articles.extend(_get_yfinance_news(ticker))  # First 10 articles
    news_articles.extend(_get_finviz_news(ticker))     # First 10 articles
    
        # Analyze sentiment
    return _analyze_sentiment(news_articles)
    
def _get_yfinance_news(self, ticker: str):
    """Get news from Yahoo Finance using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        articles = []
        for article in news[:30]:  # Get the 5 most recent articles
            try:
                article_data = {
                    'title': article['content']['title'],
                    'source': 'Yahoo Finance'
                }
                articles.append(article_data)
            except KeyError as e:
                print(f"Malformed article data, missing key: {str(e)}")
                continue
        
        return articles
    except Exception as e:
        print(f"Yahoo Finance error: {str(e)}")
        return []
    
def _get_finviz_news(self, ticker: str):
    """Get news from Finviz"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_table = soup.find(id='news-table')
        if not news_table:
            return []
        
        articles = []
        for row in news_table.find_all('tr'):
            title = row.a.text if row.a else 'No title'
            articles.append({
                'title': title,
                'source': 'Finviz',
            })
            if len(articles) >= 30 :
                break
        return articles
    except Exception as e:
        print(f"Finviz error: {str(e)}")
        return []
    
def _analyze_sentiment(articles):
    """Analyze sentiment from collected articles"""
    if not articles:
        return {
            'average_sentiment': 0,
            'positive_articles': 0,
            'neutral_articles': 0,
            'negative_articles': 0,
            'total_articles': 0,
            'sources': [],
            'sentiment_interpretation': 'No Data'
        }
    
    sentiments = []
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    sources = set()
    
    for article in articles:
        text = article['title']  # Use title for sentiment analysis
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        sentiments.append(sentiment)
        
        # Categorize sentiment
        if sentiment > 0.2:
            sentiment_counts['positive'] += 1
        elif sentiment < -0.2:
            sentiment_counts['negative'] += 1
        else:
            sentiment_counts['neutral'] += 1
        
        sources.add(article.get('source', 'Unknown'))
    
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    
    return {
        'average_sentiment': round(avg_sentiment, 3),
        'positive_articles': sentiment_counts['positive'],
        'neutral_articles': sentiment_counts['neutral'],
        'negative_articles': sentiment_counts['negative'],
        'total_articles': len(articles),
        'sources': list(sources),
        'sentiment_interpretation': _interpret_sentiment(avg_sentiment)
    }

def _interpret_sentiment(score: float) -> str:
    """Convert sentiment score to human-readable interpretation"""
    if score > 0.3:
        return "Strongly Positive"
    elif score > 0.1:
        return "Positive"
    elif score < -0.3:
        return "Strongly Negative"
    elif score < -0.1:
        return "Negative"
    else:
        return "Neutral"
