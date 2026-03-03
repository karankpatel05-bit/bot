import os
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from predictor import predict_movement, analyze_holding
import portfolio_manager
from screener import run_screener

# Load Environment Variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_text = (
        "📈 *Welcome to TradeBot!* 📉\n\n"
        "I can predict the movement of stocks based on Technical Chart Data "
        "(RSI, MACD) and Recent News Sentiment (FinBERT).\n\n"
        "Try sending me: `/analyze <TICKER>`\n"
        "Example: `/analyze RELIANCE`"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 *TradeBot Help*\n\n"
        "Commands:\n"
        "`/start` - Welcome message\n"
        "`/analyze <TICKER>` - Get prediction for a stock\n"
        "`/help` - Show this help message"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze the given ticker symbol."""
    if not context.args:
        await update.message.reply_text("Please provide a ticker symbol. Example: `/analyze RELIANCE`", parse_mode='Markdown')
        return

    ticker = context.args[0].upper()
    await update.message.reply_text(f"🔍 Analyzing {ticker}... This might take a few seconds.", parse_mode='Markdown')

    prediction_data = predict_movement(ticker)

    if "error" in prediction_data:
        await update.message.reply_text(f"❌ *Error:*\n{prediction_data['error']}", parse_mode='Markdown')
        return

    # Format output
    try:
        response_text = (
            f"📊 *Analysis for {prediction_data['symbol']}*\n\n"
            f"💵 *Current Price:* ${prediction_data['current_price']:.2f}\n"
            f"📈 *Volume:* {prediction_data['volume']:,.0f}\n\n"
            f"🛠 *Technicals (EMA/BB/RSI/MACD)*\n"
            f"• RSI: {prediction_data['rsi']:.2f}\n"
            f"• MACD Hist: {prediction_data['macd_hist']:.4f}\n"
            f"• Price vs EMA50: {'Above' if prediction_data['current_price'] > prediction_data['ema_50'] else 'Below'}\n\n"
            f"📰 *Firm News Sentiment:* {prediction_data['sentiment']}\n"
            f"🌍 *Global Macro Sentiment:* {prediction_data['global_sentiment']}\n\n"
            f"🎯 *Final Prediction:* {prediction_data['prediction']} (Score: {prediction_data['score']})"
        )
    except Exception as e:
        response_text = f"❌ *Error formatting response:* {e}\nRaw Data: {prediction_data}"

    await update.message.reply_text(response_text, parse_mode='Markdown')

async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View current portfolio and get recommendations."""
    await update.message.reply_text("💼 *Loading Portfolio... Analyzing holdings!*", parse_mode='Markdown')
    holdings = portfolio_manager.get_holdings()
    
    if not holdings:
        await update.message.reply_text("Your portfolio is empty. Add stocks using `/add <TICKER> <QTY> <PRICE>`.", parse_mode='Markdown')
        return

    response_text = "💼 *Your Portfolio & Recommendations:*\n\n"
    total_value = 0
    total_cost = 0

    for ticker, info in holdings.items():
        qty = info['qty']
        avg_price = info['avg_price']
        
        analysis = analyze_holding(ticker, avg_price)
        if "error" in analysis:
            response_text += f"• *{ticker}*: Error analyzing data.\n"
            continue

        current_price = analysis['current_price']
        profit_pct = analysis['profit_pct']
        rec = analysis['portfolio_recommendation']
        
        value = qty * current_price
        cost = qty * avg_price
        total_value += value
        total_cost += cost
        
        emoji = "🟢" if profit_pct > 0 else "🔴"
        response_text += (
            f"• *{ticker}*: {qty} shares @ ${avg_price:.2f} ➡️ Now ${current_price:.2f}\n"
            f"  {emoji} P&L: {profit_pct:.2f}% | 💡 *Action:* {rec}\n\n"
        )
        
    total_pl_pct = ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    overall_emoji = "🟢" if total_pl_pct > 0 else "🔴"
    response_text += f"---\n*Total Value:* ${total_value:.2f}\n*Overall P&L:* {overall_emoji} {total_pl_pct:.2f}%"
    
    await update.message.reply_text(response_text, parse_mode='Markdown')

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a holding to the portfolio."""
    if len(context.args) != 3:
        await update.message.reply_text("Usage: `/add <TICKER> <QTY> <PRICE>`\nExample: `/add RELIANCE 10 2500.50`", parse_mode='Markdown')
        return

    ticker = context.args[0]
    try:
        qty = float(context.args[1])
        price = float(context.args[2])
    except ValueError:
        await update.message.reply_text("Quantity and Price must be numbers.")
        return

    result = portfolio_manager.add_holding(ticker, qty, price)
    await update.message.reply_text(result)

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a holding from the portfolio."""
    if not context.args:
        await update.message.reply_text("Usage: `/remove <TICKER>`\nExample: `/remove RELIANCE`", parse_mode='Markdown')
        return

    ticker = context.args[0]
    result = portfolio_manager.remove_holding(ticker)
    await update.message.reply_text(result)

async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run the screener for fresh recommendations."""
    await update.message.reply_text("🔎 *Running Stock Screener...*\nLooking for +15% short-term gain candidates. This takes a minute!", parse_mode='Markdown')
    candidates = run_screener()
    
    if not candidates:
        await update.message.reply_text("📉 No strong candidates found right now. Market might be choppy.")
        return
        
    response_text = "🌟 *Top Screener Recommendations:*\n\n"
    for c in candidates[:5]: # Show top 5
        response_text += f"• *{c['ticker']}* @ ${c['price']:.2f} (Score: {c['score']})\n  RSI: {c['rsi']:.1f}\n  {c['reason']}\n\n"
        
    await update.message.reply_text(response_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages using basic keyword/intent matching."""
    text = update.message.text.lower()
    
    # 1. Intent: Portfolio
    if any(word in text for word in ["portfolio", "holdings", "my stocks", "positions", "how am i doing"]):
        await portfolio_command(update, context)
        return
        
    # 2. Intent: Recommendations
    if any(word in text for word in ["recommend", "suggest", "what to buy", "screener", "top stocks", "picks"]):
        await recommend_command(update, context)
        return
        
    # 3. Intent: Analyze a specific stock
    # Look for a ticker symbol (typically uppercase words in the original text)
    original_words = update.message.text.split()
    tickers = []
    
    for w in original_words:
        clean_w = re.sub(r'[^\w\s]', '', w)
        # If it's all uppercase and at least 2 chars, it's likely a ticker
        if clean_w.isupper() and len(clean_w) >= 2:
            tickers.append(clean_w)
            
    # If no uppercase tickers found, check the words following certain keywords
    if not tickers:
        words = text.split()
        keywords = ["analyze", "check", "predict", "about", "for", "buy", "sell", "is", "chart"]
        for i, w in enumerate(words):
            if w in keywords and i + 1 < len(words):
                clean_target = re.sub(r'[^\w\s]', '', words[i+1]).upper()
                # Exclude common stop words that might follow these keywords
                if len(clean_target) > 1 and clean_target not in ["A", "THE", "THIS", "THAT", "MY", "SOME", "GOOD", "BAD"]:
                    tickers.append(clean_target)
                    break
                    
    if tickers:
        # Mock context.args so analyze_command can process it
        context.args = [tickers[0]]
        await analyze_command(update, context)
        return
        
    # Fallback
    fallback_text = (
        "I'm not exactly sure what you mean! 🤔\n\n"
        "Try saying things like:\n"
        "- *\"Analyze TCS\"*\n"
        "- *\"How is RELIANCE looking?\"*\n"
        "- *\"Show my portfolio\"*\n"
        "- *\"Can you recommend some stocks?\"*"
    )
    await update.message.reply_text(fallback_text, parse_mode='Markdown')

def main():
    """Start the bot."""
    if not TOKEN or TOKEN == "your_token_here":
        print("Error: TELEGRAM_BOT_TOKEN not found or not set in .env file.")
        return

    # Create the Application and pass it your bot's token.
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analyze", analyze_command))
    app.add_handler(CommandHandler("portfolio", portfolio_command))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("remove", remove_command))
    app.add_handler(CommandHandler("recommend", recommend_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    print("Bot is up and running. Press Ctrl-C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
