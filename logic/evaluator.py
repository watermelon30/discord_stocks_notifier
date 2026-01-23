import pandas as pd
from indicators.momentum import RSIIndicator, RCIIndicator
from indicators.trend import EMAIndicator

def evaluate_group(close_series: pd.Series, group_config: dict) -> tuple[bool, str, dict]:
    """
    Evaluates conditions and returns (is_triggered, description, stats).
    Included stats: Price, RSI, RCI, and any EMA used in conditions.
    """
    if close_series.empty:
        return False, "", {}
        
    group_name = group_config.get("name", "Unnamed Group")
    conditions = group_config.get("conditions", [])
    if not conditions:
        return False, "", {}
        
    logic = group_config.get("logic", "AND")
    results = []
    messages = []
    stats = {"Price": round(close_series.iloc[-1], 2)} 
    
    current_price = close_series.iloc[-1]
    
    for cond in conditions:
        ind_type = cond.get("indicator")
        period = int(cond.get("period", 14))
        operator = cond.get("operator", "<")
        val = cond.get("value")
        
        met = False
        msg = ""
        try:
            if ind_type == "RSI":
                rsi_series = RSIIndicator(period=period).calculate(close_series)
                curr_rsi = round(rsi_series.iloc[-1], 2)
                stats['RSI'] = curr_rsi
                threshold = float(val)
                met = (curr_rsi < threshold) if operator == "<" else (curr_rsi > threshold)
                msg = f"RSI {operator} {int(threshold)}"
                    
            elif ind_type == "RCI":
                rci_series = RCIIndicator(period=period).calculate(close_series)
                curr_rci = round(rci_series.iloc[-1], 2)
                stats['RCI'] = curr_rci
                threshold = float(val)
                met = (curr_rci < threshold) if operator == "<" else (curr_rci > threshold)
                msg = f"RCI {operator} {int(threshold)}"
            
            elif ind_type == "Price vs EMA":
                ema_series = EMAIndicator(period=period).calculate(close_series)
                curr_ema = round(ema_series.iloc[-1], 2)
                stats[f'EMA({period})'] = curr_ema
                met = (current_price < curr_ema) if operator == "<" else (current_price > curr_ema)
                msg = f"Price {operator} EMA({period})"
            
            results.append(met)
            if met:
                messages.append(msg)
                
        except Exception as e:
            print(f"Eval error for {ind_type}: {e}")
            results.append(False)

    is_triggered = all(results) if logic == "AND" else any(results)
    
    if is_triggered:
        desc = f"[{group_name}] " + (", ".join(messages) if logic == "AND" else " || ".join(messages))
        return True, desc, stats
    
    return False, "", {}

# --- EXAMPLE USAGE ---
# triggered_data = []
# for ticker, data in stock_data_dict.items():
#     triggered, description, stats = evaluate_group(data['close'], my_config)
#     if triggered:
#         stats['Ticker'] = ticker
#         triggered_data.append(stats)
# 
# discord_message = f"**Alert Triggered!**\n{description}\n" + format_discord_table(triggered_data)