# 📈 Pro Stock Notifier

A highly customizable, local-first stock market alert system. Monitor technical indicators (RSI, RCI, EMA, Days Above EMA) and get notified via Discord when your specific conditions are met.

## Features

- **Custom Alert Rules**: Build complex rules using logical grouping (AND/OR).
- **Flexible Indicators**: RSI, RCI, Price vs EMA, EMA Proximity, and Days Above EMA.
- **Local Persistence**: All your settings, tickers, and rules are saved locally.
- **Discord Integration**: Get real-time alerts to your server or DM.
- **Privacy First**: Webhook URL stored in `.env` (git-ignored), no external servers beyond stock data fetching.

## Quick Start

1. Clone or download this repository.
2. Create a `.env` file in the project root with your Discord webhook:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook/url
   ```
3. Double-click `run.bat` to install dependencies and start the app.

That's it. `run.bat` handles `pip install -r requirements.txt` automatically before launching Streamlit.

## Manual Setup

If you prefer running manually:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Usage

1. **Configure Settings (Sidebar)**:
   - Add the tickers you want to watch.
   - The Discord Webhook URL is loaded from your `.env` file. You can also override it in the sidebar.
2. **Create Rules**:
   - Click "Add New Rule Group".
   - Select Logic: **AND** (all conditions must be met) or **OR** (any condition triggers).
   - Add Conditions (e.g., RSI < 30, Price < EMA 200, Days Above EMA(7) >= 7).
3. **Run Analysis**:
   - Click "Run Analysis" in the main view.
   - Results will be grouped by your Rule Groups and sent to Discord.

## Configuration

- **Rules & Tickers**: Saved in `config.json` (safe to commit).
- **Webhook URL**: Stored in `.env` (git-ignored, never committed).

## Project Structure

```
app.py                  # Streamlit UI orchestrator
logic/
  evaluator.py          # Condition evaluation engine
  runner.py             # Analysis orchestration (fetch → evaluate)
indicators/
  base.py               # Abstract indicator base class
  momentum.py           # RSI, RCI indicators
  trend.py              # EMA indicators
utils/
  config.py             # Config load/save with .env integration
  discord_sender.py     # Discord messaging and batching
  formatting.py         # Discord table formatting
data/
  fetcher.py            # yfinance data fetching
```

## Contributing

Feel free to add more indicators in `indicators/` — just extend the `Indicator` base class and add evaluation logic in `logic/evaluator.py`.
