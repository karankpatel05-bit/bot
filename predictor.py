from data_fetcher import get_ticker_data, fetch_global_news
from sentiment_analyzer import analyze_sentiment
import pandas as pd

def predict_movement(ticker: str) -> dict:
    """
    Combines technical indicators and sentiment to predict
    whether a stock is going UP, DOWN, or sideways (NEUTRAL).
    """
    try:
        data = get_ticker_data(ticker)
    except Exception as e:
        return {"error": f"Failed to fetch data for {ticker}. Error: {e}"}

    if not data:
        return {"error": f"No data found for {ticker}."}

    # Analyze Sentiment
    sentiment = analyze_sentiment(data['recent_news'])

    # Analyze Global Sentiment
    global_news = fetch_global_news()
    global_sentiment = analyze_sentiment(global_news)

    # Analyze RSI (Typical oversold < 30, overbought > 70)
    rsi = data['rsi']
    if pd.isna(rsi):
        rsi_signal = "Neutral"
    elif rsi < 30:
        rsi_signal = "Bullish"
    elif rsi > 70:
        rsi_signal = "Bearish"
    else:
        rsi_signal = "Neutral"

    # Analyze MACD (Typical bullish if histogram > 0)
    macd_hist = data['macd_hist']
    if pd.isna(macd_hist):
        macd_signal = "Neutral"
    elif macd_hist > 0:
        macd_signal = "Bullish"
    else:
        macd_signal = "Bearish"

    # Analyze EMA Trend
    ema20 = data['ema_20']
    ema50 = data['ema_50']
    current_price = data['current_price']
    
    if pd.isna(ema20) or pd.isna(ema50):
        ema_signal = "Neutral"
    elif current_price > ema20 and ema20 > ema50:
        ema_signal = "Bullish"
    elif current_price < ema20 and ema20 < ema50:
        ema_signal = "Bearish"
    else:
        ema_signal = "Neutral"
        
    # Analyze Bollinger Bands
    bb_low = data['bb_low']
    bb_high = data['bb_high']
    if pd.isna(bb_low) or pd.isna(bb_high):
        bb_signal = "Neutral"
    elif current_price <= bb_low * 1.02: # Within 2% of bottom band
        bb_signal = "Bullish" # Reversal expected
    elif current_price >= bb_high * 0.98: # Within 2% of top band
        bb_signal = "Bearish" # Reversal expected
    else:
        bb_signal = "Neutral"

    # Consolidate signals (Including global sentiment with half weight)
    score = 0
    signals = [sentiment, rsi_signal, macd_signal, ema_signal, bb_signal]
    
    for sig in signals:
        if sig == "Bullish":
            score += 1
        elif sig == "Bearish":
            score -= 1
            
    # Add half-weight for global sentiment
    if global_sentiment == "Bullish":
        score += 0.5
    elif global_sentiment == "Bearish":
        score -= 0.5

    if score > 1.5:
        prediction = "UP 📈"
    elif score < -1.5:
        prediction = "DOWN 📉"
    else:
        prediction = "NEUTRAL ↔️"

    return {
        "symbol": data['symbol'],
        "current_price": current_price,
        "volume": data['volume'],
        "rsi": rsi,
        "macd_hist": macd_hist,
        "ema_20": ema20,
        "ema_50": ema50,
        "sentiment": sentiment,
        "global_sentiment": global_sentiment,
        "prediction": prediction,
        "score": score
    }

def analyze_holding(ticker: str, avg_price: float) -> dict:
    """
    Evaluates a specific portfolio holding to recommend BUY, SELL, or HOLD.
    """
    prediction_data = predict_movement(ticker)
    if "error" in prediction_data:
        return prediction_data

    current_price = prediction_data['current_price']
    profit_pct = ((current_price - avg_price) / avg_price) * 100
    score = prediction_data.get('score', 0)
    
    # Simple recommendation logic
    if profit_pct > 15 and score < 0:
        # Take profit if up 15% and trend is turning bearish
        recommendation = "SELL (Take Profit)"
    elif profit_pct < -10 and score < -2:
        # Cut losses if down 10% and strongly bearish
        recommendation = "SELL (Cut Losses)"
    elif score > 2:
        # Strong uptrend
        recommendation = "BUY (Add to position)"
    else:
        recommendation = "HOLD"

    prediction_data['avg_price'] = avg_price
    prediction_data['profit_pct'] = profit_pct
    prediction_data['portfolio_recommendation'] = recommendation
    return prediction_data
