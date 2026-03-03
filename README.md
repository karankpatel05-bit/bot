# TradeBot (Telegram)

TradeBot is a Telegram bot that predicts stock movement (UP or DOWN) by analyzing:
1. Technical Chart Data (Price, Volume, RSI, MACD Histogram)
2. Recent News Sentiment (using FinBERT for NLP analysis)

## Prerequisites
- Python 3.10+ (Ubuntu 22.04 default)
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather) on Telegram)

## Installation

1. Clone or navigate to the repository:
   ```bash
   cd /home/karan/j/tradebot
   ```

2. Activate the virtual environment (created automatically during setup):
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   pip install -r requirements.txt
   ```
   *Note: We use the CPU version of PyTorch to save space and time if a GPU is not available.*

4. Configure your `.env` file:
   Rename `.env.example` to `.env` and add your Telegram bot token:
   ```bash
   cp .env.example .env
   nano .env
   # Add your token: TELEGRAM_BOT_TOKEN=123456789:ABCDEF...
   ```

## Running the Bot

Run the main script to start the bot polling:
```bash
python main.py
```

The console should say `Bot is up and running. Press Ctrl-C to stop.`

Open Telegram and send a message to your bot:
- `/start` to see the welcome message
- `/analyze AAPL` to analyze Apple stock (or any other ticker symbol supported by Yahoo Finance)

## Deployment (Run in Background)
To keep the bot running after you close your terminal, you can use `tmux` or `screen`:
```bash
tmux new -s tradebot
cd /home/karan/j/tradebot
source venv/bin/activate
python main.py
```
*(Press `Ctrl+B` then `D` to detach and leave it running in the background).*
# bot
# bot
