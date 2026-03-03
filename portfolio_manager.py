import json
import os

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio() -> dict:
    if not os.path.exists(PORTFOLIO_FILE):
        return {}
    try:
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading portfolio: {e}")
        return {}

def save_portfolio(portfolio: dict):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=4)

def add_holding(ticker: str, qty: float, avg_price: float) -> str:
    ticker = ticker.upper()
    portfolio = load_portfolio()
    
    # Simple overwrite or addition rules can apply. 
    # For now, we'll just overwrite an existing entry for simplicity.
    portfolio[ticker] = {
        "qty": qty,
        "avg_price": avg_price
    }
    save_portfolio(portfolio)
    return f"Successfully added {qty} shares of {ticker} at ${avg_price:.2f}."

def remove_holding(ticker: str) -> str:
    ticker = ticker.upper()
    portfolio = load_portfolio()
    if ticker in portfolio:
        del portfolio[ticker]
        save_portfolio(portfolio)
        return f"Successfully removed {ticker} from portfolio."
    return f"{ticker} is not in your portfolio."

def get_holdings() -> dict:
    return load_portfolio()
