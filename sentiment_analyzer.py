from transformers import pipeline

def analyze_sentiment(news_list: list) -> str:
    """
    Analyzes list of news headline strings using ProsusAI/finbert.
    Returns: 'Bullish', 'Bearish', or 'Neutral'.
    """
    if not news_list:
        return "Neutral"

    # Initialize FinBERT pipeline
    # Note: Device=-1 uses CPU explicitly. Change to >0 for GPU if available.
    try:
        classifier = pipeline("sentiment-analysis", model="ProsusAI/finbert", device=-1)
    except Exception as e:
        print(f"Error loading FinBERT model: {e}")
        return "Neutral"

    results = classifier(news_list)

    # Tally up the sentiment
    score_map = {"positive": 1, "negative": -1, "neutral": 0}
    total_score = sum(score_map.get(res['label'], 0) for res in results)
    
    if total_score > 0:
        return "Bullish"
    elif total_score < 0:
        return "Bearish"
    else:
        return "Neutral"

if __name__ == "__main__":
    test_news = [
        "Apple reports record quarterly earnings",
        "Apple faces declining sales in China",
        "Apple announces new AI initiative"
    ]
    print(f"Test Score: {analyze_sentiment(test_news)}")
