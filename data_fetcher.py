import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta

import feedparser

def fetch_global_news() -> list:
    """
    Fetches top global business/finance news from Yahoo Finance RSS.
    Returns a list of headline strings.
    """
    rss_url = "https://finance.yahoo.com/news/rssindex"
    try:
        feed = feedparser.parse(rss_url)
        headlines = []
        for entry in feed.entries[:5]: # Top 5 global news
            if 'title' in entry:
                headlines.append(entry.title)
        return headlines
    except Exception as e:
        print(f"Error fetching global news: {e}")
        return []

def get_ticker_data(ticker_symbol: str):
    """
    Fetches historical data, calculates RSI, MACD, EMAs, Bollinger Bands
    and gets recent news for the ticker.
    """
    # Automatically append .NS for Indian stocks if no suffix is provided
    if not ticker_symbol.endswith('.NS') and not ticker_symbol.endswith('.BO'):
        ticker_symbol = f"{ticker_symbol}.NS"
        
    ticker = yf.Ticker(ticker_symbol)
    
    # Get 6 months of historical data to calculate technicals reliably
    hist_data = ticker.history(period="6mo")
    if hist_data.empty:
        return None

    # Calculate RSI
    hist_data['RSI'] = ta.momentum.RSIIndicator(close=hist_data['Close'], window=14).rsi()
    
    # Calculate MACD
    macd = ta.trend.MACD(close=hist_data['Close'])
    hist_data['MACD'] = macd.macd()
    hist_data['MACD_Signal'] = macd.macd_signal()
    hist_data['MACD_Hist'] = macd.macd_diff()

    # Calculate EMAs
    hist_data['EMA_20'] = ta.trend.EMAIndicator(close=hist_data['Close'], window=20).sma_indicator()
    hist_data['EMA_50'] = ta.trend.EMAIndicator(close=hist_data['Close'], window=50).sma_indicator()

    # Calculate Bollinger Bands
    bollinger = ta.volatility.BollingerBands(close=hist_data['Close'], window=20, window_dev=2)
    hist_data['BB_High'] = bollinger.bollinger_hband()
    hist_data['BB_Low'] = bollinger.bollinger_lband()
    hist_data['BB_Mid'] = bollinger.bollinger_mavg()

    # Get latest data point
    latest_data = hist_data.iloc[-1]
    
    # Try to grab fast info for Bid/Ask but fallback to Close if missing
    try:
        info = ticker.fast_info
        current_price = info.last_price
        volume = info.last_volume
    except:
        current_price = latest_data['Close']
        volume = latest_data['Volume']

    # Fetch recent news
    news_items = ticker.news
    recent_news = []
    if news_items:
        # Take up to 5 latest news items
        for n in news_items[:5]:
            title = n.get('title', '')
            publisher = n.get('publisher', '')
            if title:
                recent_news.append(f"{publisher}: {title}")

    return {
        'symbol': ticker_symbol.upper(),
        'current_price': current_price,
        'volume': volume,
        'rsi': latest_data['RSI'],
        'macd': latest_data['MACD'],
        'macd_signal': latest_data['MACD_Signal'],
        'macd_hist': latest_data['MACD_Hist'],
        'ema_20': latest_data['EMA_20'],
        'ema_50': latest_data['EMA_50'],
        'bb_high': latest_data['BB_High'],
        'bb_low': latest_data['BB_Low'],
        'bb_mid': latest_data['BB_Mid'],
        'recent_news': recent_news
    }

if __name__ == "__main__":
    # Test
    data = get_ticker_data('AAPL')
    print("Test Output for AAPL:")
    for key, val in data.items():
        print(f"{key}: {val}")
