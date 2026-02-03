import streamlit as st
import pandas as pd
from data.fetcher import fetch_stock_data
from utils.discord_sender import send_discord_message
from utils.config import load_config, save_config
from logic.evaluator import evaluate_group

# Page Config
st.set_page_config(page_title="Stock Notifier", layout="wide")
st.title("📈 Pro Stock Notifier")

# Load Config
if "config" not in st.session_state:
    st.session_state.config = load_config()

config = st.session_state.config

def save_current_config():
    save_config(st.session_state.config)

    
def format_discord_table(matches: list[dict]) -> str:
    """
    Generates a monospaced ASCII table for Discord.
    matches: list of dicts containing ticker and indicator stats.
    """
    if not matches:
        return "No matches found."

    # Define Column Order: Ticker first, then Price, then RSI/RCI, then any EMAs
    all_keys = set().union(*(m.keys() for m in matches))
    ema_cols = sorted([k for k in all_keys if "EMA" in k])
    
    # Static priority headers
    headers = ["Ticker", "Price"]
    if "RSI" in all_keys: headers.append("RSI")
    if "RCI" in all_keys: headers.append("RCI")
    headers.extend(ema_cols)
    
    # Calculate column widths based on longest string in header or data
    widths = {h: len(h) for h in headers}
    for m in matches:
        for h in headers:
            val = str(m.get(h, "-"))
            widths[h] = max(widths[h], len(val))

    def make_row(row_data):
        return "| " + " | ".join(str(row_data.get(h, "-")).ljust(widths[h]) for h in headers) + " |"

    def make_separator():
        return "+" + "+".join("-" * (widths[h] + 2) for h in headers) + "+"

    # Construct table
    table_lines = [make_separator(), make_row({h: h for h in headers}), make_separator()]
    for m in matches:
        table_lines.append(make_row(m))
    table_lines.append(make_separator())

    return "```\n" + "\n".join(table_lines) + "\n```"


# --- Sidebar ---
with st.sidebar:
    st.header("Global Settings")
    
    # Tickers
    current_tickers = ", ".join(config.get("tickers", []))
    new_tickers = st.text_area("Tickers (comma separated)", value=current_tickers, height=100)
    if new_tickers != current_tickers:
        raw_list = [t.strip().upper() for t in new_tickers.split(",") if t.strip()]
        unique_tickers = list(dict.fromkeys(raw_list))
        config["tickers"] = unique_tickers
        save_current_config()
        
    # Webhook
    current_webhook = config.get("webhook_url", "")
    new_webhook = st.text_input("Discord Webhook URL", value=current_webhook, type="password")
    if new_webhook != current_webhook:
        config["webhook_url"] = new_webhook
        save_current_config()
        
    st.divider()
    st.header("Alert Rules")
    
    # Add New Group
    if st.button("➕ Add New Rule Group"):
        new_group = {
            "name": f"New Group {len(config.get('groups', [])) + 1}",
            "logic": "AND",
            "conditions": []
        }
        config.setdefault("groups", []).append(new_group)
        save_current_config()
        st.rerun()

    # Manage Groups
    groups = config.get("groups", [])
    groups_to_remove = []
    
    for i, group in enumerate(groups):
        with st.expander(f"📂 {group.get('name', 'Unnamed')}", expanded=False):
            # Group Name
            new_name = st.text_input("Group Name", value=group.get("name", ""), key=f"g_name_{i}")
            if new_name != group.get("name"):
                group["name"] = new_name
                save_current_config()
            
            # Logic
            current_logic = group.get("logic", "AND")
            new_logic = st.selectbox("Trigger Logic", ["AND", "OR"], index=0 if current_logic == "AND" else 1, key=f"g_logic_{i}")
            if new_logic != current_logic:
                group["logic"] = new_logic
                save_current_config()
            
            st.caption(f"Triggers if **{new_logic}** conditions are met.")
            
            # Conditions
            st.subheader("Conditions")
            conditions = group.get("conditions", [])
            conds_to_remove = []
            
            for j, cond in enumerate(conditions):
                c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1, 1.5, 0.5])
                
                # Indicator Type
                with c1:
                    ind_types = ["RSI", "RCI", "Price vs EMA", "EMA Proximity"]
                    curr_type = cond.get("indicator", "RSI")
                    new_type = st.selectbox("Indicator", ind_types, index=ind_types.index(curr_type) if curr_type in ind_types else 0, key=f"c_type_{i}_{j}", label_visibility="collapsed")
                    if new_type != curr_type:
                        cond["indicator"] = new_type
                        save_current_config()
                        st.rerun()

                # Period
                with c2:
                    ema_periods = [7, 13, 21, 55, 100, 200] 
                    osc_periods = [9, 14, 21, 30, 50]
                    current_period = cond.get("period", 14)
                    if new_type in ["Price vs EMA", "EMA Proximity"]:
                        new_period = st.selectbox(
                            "Period", 
                            ema_periods, 
                            index=ema_periods.index(current_period) if current_period in ema_periods else 5, 
                            key=f"c_per_{i}_{j}", 
                            label_visibility="collapsed"
                        )
                    elif new_type in ["RSI", "RCI"]:
                        new_period = st.selectbox(
                            "Period", 
                            osc_periods, 
                            index=osc_periods.index(current_period) if current_period in osc_periods else 1, # Default to 14
                            key=f"c_per_{i}_{j}", 
                            label_visibility="collapsed"
                        )
                    else:
                        # Fallback for any other indicators
                        new_period = st.number_input(
                            "Period", 
                            value=int(current_period), 
                            min_value=1, 
                            key=f"c_per_{i}_{j}", 
                            label_visibility="collapsed"
                        )
                    if new_period != current_period:
                        cond["period"] = new_period
                        save_current_config()

                # Operator
                with c3:
                    if new_type == "EMA Proximity":
                        options = ["≈", ">", "<"]
                        curr_op = cond.get("operator", "=")
                        
                        current_selection_index = 0 # Default to 'within'
                        if curr_op == '>':
                            current_selection_index = 1 # 'above'
                        elif curr_op == '<':
                            current_selection_index = 2 # 'below'
                        
                        selected_option = st.selectbox(
                            "Proximity", 
                            options, 
                            index=current_selection_index, 
                            key=f"c_op_{i}_{j}", 
                            label_visibility="collapsed"
                        )
                        
                        new_op = {'≈': '=', '>': '>', '<': '<'}[selected_option]

                        if new_op != curr_op:
                            cond["operator"] = new_op
                            save_current_config()

                    else:
                        ops = ["<", ">"]
                        curr_op = cond.get("≈", "<")
                        new_op = st.selectbox("Op", ops, index=ops.index(curr_op), key=f"c_op_{i}_{j}", label_visibility="collapsed")
                        if new_op != curr_op:
                            cond["operator"] = new_op
                            save_current_config()

                # Value (Threshold)
                with c4:
                    if new_type == "Price vs EMA":
                        st.write("Current EMA") # Placeholder
                    elif new_type == "EMA Proximity":
                        curr_val = cond.get("value", 3.0)
                        new_val = st.number_input("%", value=float(curr_val), min_value=0.1, max_value=100.0, step=0.5, key=f"c_val_{i}_{j}", label_visibility="collapsed")
                        if new_val != curr_val:
                            cond["value"] = new_val
                            save_current_config()
                    else:
                        curr_val = cond.get("value", 30)
                        new_val = st.number_input("Val", value=float(curr_val), key=f"c_val_{i}_{j}", label_visibility="collapsed")
                        if new_val != curr_val:
                            cond["value"] = new_val
                            save_current_config()
                
                # Delete Condition
                with c5:
                    if st.button("🗑️", key=f"del_c_{i}_{j}"):
                        conds_to_remove.append(j)
            
            if conds_to_remove:
                for idx in sorted(conds_to_remove, reverse=True):
                    conditions.pop(idx)
                save_current_config()
                st.rerun()

            if st.button("➕ Add Condition", key=f"add_c_{i}"):
                conditions.append({"indicator": "RSI", "period": 14, "operator": "<", "value": 30})
                save_current_config()
                st.rerun()
            
            st.divider()
            if st.button("🛑 Delete Group", key=f"del_g_{i}"):
                groups_to_remove.append(i)

    if groups_to_remove:
        for idx in sorted(groups_to_remove, reverse=True):
            groups.pop(idx)
        save_current_config()
        st.rerun()

# --- Main Logic ---

if st.button("🚀 Run Analysis", type="primary"):
    tickers = config.get("tickers", [])
    groups = config.get("groups", [])
    
    if not tickers:
        st.warning("Please add some tickers in the settings.")
    elif not groups:
        st.warning("Please configure at least one rule group.")
    else:
        status = st.status("Analyzing Market Data...", expanded=True)
        
        status.write("Fetching stock data...")
        try:
            raw_data = fetch_stock_data(tickers)
            
            results_by_group = {} # { "Group Name": [ {Ticker, Price, Msg} ] }
            all_alerts_text = []

            status.write("Evaluating rules...")
            
            for ticker in tickers:
                # Extract data safely (reusing the robust logic from before)
                df = None
                try:
                    if isinstance(raw_data.columns, pd.MultiIndex):
                        if ticker in raw_data.columns.get_level_values(0):
                            df = raw_data[ticker]
                    elif len(tickers) == 1:
                        df = raw_data
                except:
                    pass
                
                if df is None or df.empty or 'Close' not in df.columns:
                    continue
                
                close_series = df['Close']
                curr_price = close_series.iloc[-1]
                
                # Check each group
                for group in groups:
                    triggered, group_title, stats = evaluate_group(close_series, group)
                    if triggered:
                        g_name = group_title
                        if g_name not in results_by_group:
                            results_by_group[g_name] = []
                        
                        # Add ticker to stats
                        stats["Ticker"] = ticker
                        results_by_group[g_name].append(stats)
            
            status.update(label="Analysis Complete!", state="complete", expanded=False)
            
            # --- Display Results ---
            if not results_by_group:
                st.info("No tickers matched any of the configured rules.")
            else:
                for g_name, matches in results_by_group.items():
                    st.subheader(f"🔔 {g_name}")
                    res_df = pd.DataFrame(matches)
                    st.table(res_df)
                    
                    # Prepare Discord text using format_discord_table
                    table_text = format_discord_table(matches)
                    group_text = f"**{g_name}**:\n{table_text}"
                    all_alerts_text.append(group_text)

                # --- Notifications ---
                if config.get("webhook_url"):
                    if all_alerts_text:
                        full_msg = "**Stock Alerts Triggered**\n\n" + "\n\n".join(all_alerts_text)
                        success, resp = send_discord_message(config["webhook_url"], full_msg)
                        if success:
                            st.toast("Discord notification sent!", icon="✅")
                        else:
                            st.error(f"Discord Error: {resp}")
                else:
                    st.warning("Notifications skipped (No Webhook URL configured).")

        except Exception as e:
            st.error(f"An error occurred: {e}")
            import traceback
            st.text(traceback.format_exc())
