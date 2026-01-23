# 📈 Pro Stock Notifier

A highly customizable, local-first stock market alert system. Monitor technical indicators (RSI, RCI, EMA) and get notified via Discord when your specific conditions are met.

## Features

- **Custom Alert Rules**: Build complex rules using logical grouping (AND/OR).
- **Flexible Indicators**: Support for RSI, RCI, and Price vs EMA logic.
- **Local Persistence**: All your settings, tickers, and rules are saved locally.
- **Discord Integration**: Get real-time alerts to your server or DM.
- **Privacy First**: No external servers (other than fetching stock data), no email login required.

## Installation

1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure `streamlit`, `pandas`, `yfinance`, `requests` are installed)*

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```
2. **Configure Settings (Sidebar)**:
   - Add the tickers you want to watch.
   - (Optional) Add your Discord Webhook URL for notifications.
3. **Create Rules**:
   - Click "Add New Rule Group".
   - Select Logic: **AND** (all conditions must be met) or **OR** (any condition triggers).
   - Add Conditions (e.g., RSI < 30, Price < EMA 200).
4. **Run Analysis**:
   - Click "Run Analysis" in the main view.
   - Results will be grouped by your Rule Groups.

## Configuration

Settings are saved efficiently in `config.json` in the root directory. You can backup this file to save your rules.

## Contributing

Feel free to modify `indicators/` to add more technical indicators!
