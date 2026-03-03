from predictor import predict_movement

# Standard list of popular tech and index-related stocks to screen
SCREENER_LIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", 
    "TSLA", "NVDA", "AMD", "NFLX", "INTC", 
    "JPM", "BAC", "V", "MA", "DIS",
    "JNJ", "PFE", "UNH", "PG", "KO"
]

def run_screener() -> list:
    """
    Scans the SCREENER_LIST to find strong buy candidates
    that have a potential +15% short-term gain based on our prediction logic.
    """
    candidates = []
    
    for ticker in SCREENER_LIST:
        print(f"Screening {ticker}...")
        try:
            prediction_data = predict_movement(ticker)
            if "error" in prediction_data:
                continue

            score = prediction_data.get('score', 0)
            rsi = prediction_data.get('rsi', 50)
            macd_hist = prediction_data.get('macd_hist', 0)
            
            # Very strong criteria: 
            # 1. Total score must be highly bullish (> 2.5)
            # 2. RSI should be coming out of oversold territory but not overbought (e.g., between 35 and 60)
            # 3. MACD histogram must be positive (upward momentum)
            is_strong_buy = score > 2.5 and (35 <= rsi <= 60) and macd_hist > 0

            if is_strong_buy:
                candidates.append({
                    "ticker": ticker,
                    "price": prediction_data['current_price'],
                    "score": score,
                    "rsi": rsi,
                    "reason": "Strong technical and sentiment alignment for a short-term pop."
                })
        except Exception as e:
            print(f"Error screening {ticker}: {e}")

    # Sort candidates by score descending
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates
