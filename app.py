import streamlit as st
import pandas as pd
from utils.config import load_config, save_config
from utils.formatting import format_discord_table
from utils.discord_sender import send_batched_notifications
from logic.runner import run_analysis

# Page Config
st.set_page_config(page_title="Stock Notifier", layout="wide")
st.title("📈 Pro Stock Notifier")

# Load Config
if "config" not in st.session_state:
    st.session_state.config = load_config()

config = st.session_state.config


def save_current_config():
    save_config(st.session_state.config)


# --- Sidebar Helper Functions ---

def render_tickers_input():
    """Render the ticker categories editor in the sidebar."""
    st.subheader("Ticker Categories")
    categories = config.get("ticker_categories", {})

    # Add new category
    with st.form("add_category_form", clear_on_submit=True):
        new_cat_name = st.text_input("New category name", label_visibility="collapsed", placeholder="New category name...")
        submitted = st.form_submit_button("➕ Add Category")
        if submitted and new_cat_name.strip() and new_cat_name.strip() not in categories:
            categories[new_cat_name.strip()] = []
            config["ticker_categories"] = categories
            save_current_config()
            st.rerun()

    # Render each category
    cats_to_remove = []
    for cat_name in list(categories.keys()):
        with st.expander(f"🏷️ {cat_name} ({len(categories[cat_name])})", expanded=True):
            # Editable category name
            new_cat_name = st.text_input(
                "Category Name", value=cat_name,
                key=f"cat_name_{cat_name}", label_visibility="collapsed"
            )
            if new_cat_name != cat_name and new_cat_name.strip():
                # Rename: preserve order by rebuilding the dict
                new_categories = {}
                for k, v in categories.items():
                    if k == cat_name:
                        new_categories[new_cat_name.strip()] = v
                    else:
                        new_categories[k] = v
                config["ticker_categories"] = new_categories
                save_current_config()
                st.rerun()

            current_tickers = ", ".join(categories[cat_name])
            new_tickers = st.text_area(
                "Tickers (comma separated)",
                value=current_tickers,
                height=68,
                key=f"cat_tickers_{cat_name}"
            )
            if new_tickers != current_tickers:
                raw_list = [t.strip().upper() for t in new_tickers.split(",") if t.strip()]
                unique_tickers = list(dict.fromkeys(raw_list))
                categories[cat_name] = unique_tickers
                config["ticker_categories"] = categories
                save_current_config()

            if st.button("🗑️ Delete Category", key=f"del_cat_{cat_name}"):
                cats_to_remove.append(cat_name)

    if cats_to_remove:
        for cat in cats_to_remove:
            del categories[cat]
        config["ticker_categories"] = categories
        save_current_config()
        st.rerun()


def render_webhook_input():
    """Render the Discord webhook URL input and persist changes."""
    current_webhook = config.get("webhook_url", "")
    new_webhook = st.text_input("Discord Webhook URL", value=current_webhook, type="password")
    if new_webhook != current_webhook:
        config["webhook_url"] = new_webhook
        save_current_config()


def render_condition_indicator(cond, i, j):
    """Render the indicator type selector for a condition."""
    ind_types = ["RSI", "RCI", "Price vs EMA", "EMA Proximity", "Days Above EMA"]
    curr_type = cond.get("indicator", "RSI")
    new_type = st.selectbox(
        "Indicator", ind_types,
        index=ind_types.index(curr_type) if curr_type in ind_types else 0,
        key=f"c_type_{i}_{j}", label_visibility="collapsed"
    )
    if new_type != curr_type:
        cond["indicator"] = new_type
        save_current_config()
        st.rerun()
    return new_type


def render_condition_period(cond, new_type, i, j):
    """Render the period selector appropriate for the indicator type."""
    ema_periods = [7, 13, 21, 55, 100, 200]
    osc_periods = [9, 14, 21, 30, 50]
    current_period = cond.get("period", 14)

    if new_type in ["Price vs EMA", "EMA Proximity", "Days Above EMA"]:
        new_period = st.selectbox(
            "Period", ema_periods,
            index=ema_periods.index(current_period) if current_period in ema_periods else 0,
            key=f"c_per_{i}_{j}", label_visibility="collapsed"
        )
    elif new_type in ["RSI", "RCI"]:
        new_period = st.selectbox(
            "Period", osc_periods,
            index=osc_periods.index(current_period) if current_period in osc_periods else 1,
            key=f"c_per_{i}_{j}", label_visibility="collapsed"
        )
    else:
        new_period = st.number_input(
            "Period", value=int(current_period), min_value=1,
            key=f"c_per_{i}_{j}", label_visibility="collapsed"
        )

    if new_period != current_period:
        cond["period"] = new_period
        save_current_config()


def render_condition_operator(cond, new_type, i, j):
    """Render the operator selector appropriate for the indicator type."""
    if new_type == "EMA Proximity":
        options = ["≈", ">", "<"]
        curr_op = cond.get("operator", "=")

        current_selection_index = 0
        if curr_op == '>':
            current_selection_index = 1
        elif curr_op == '<':
            current_selection_index = 2

        selected_option = st.selectbox(
            "Proximity", options,
            index=current_selection_index,
            key=f"c_op_{i}_{j}", label_visibility="collapsed"
        )

        new_op = {'≈': '=', '>': '>', '<': '<'}[selected_option]
        if new_op != curr_op:
            cond["operator"] = new_op
            save_current_config()
    elif new_type == "Days Above EMA":
        ops = [">=", "<="]
        curr_op = cond.get("operator", ">=")
        new_op = st.selectbox(
            "Op", ops, index=ops.index(curr_op) if curr_op in ops else 0,
            key=f"c_op_{i}_{j}", label_visibility="collapsed"
        )
        if new_op != curr_op:
            cond["operator"] = new_op
            save_current_config()
    else:
        ops = ["<", ">"]
        curr_op = cond.get("operator", "<")
        new_op = st.selectbox(
            "Op", ops, index=ops.index(curr_op) if curr_op in ops else 0,
            key=f"c_op_{i}_{j}", label_visibility="collapsed"
        )
        if new_op != curr_op:
            cond["operator"] = new_op
            save_current_config()


def render_condition_value(cond, new_type, i, j):
    """Render the threshold/value input appropriate for the indicator type."""
    if new_type == "Price vs EMA":
        st.write("Current EMA")
    elif new_type == "EMA Proximity":
        curr_val = cond.get("value", 3.0)
        new_val = st.number_input(
            "%", value=float(curr_val), min_value=0.1, max_value=100.0, step=0.5,
            key=f"c_val_{i}_{j}", label_visibility="collapsed"
        )
        if new_val != curr_val:
            cond["value"] = new_val
            save_current_config()
    elif new_type == "Days Above EMA":
        curr_val = cond.get("value", 7)
        new_val = st.number_input(
            "Days", value=int(curr_val), min_value=1, max_value=365, step=1,
            key=f"c_val_{i}_{j}", label_visibility="collapsed"
        )
        if new_val != curr_val:
            cond["value"] = new_val
            save_current_config()
    else:
        curr_val = cond.get("value", 30)
        new_val = st.number_input(
            "Val", value=float(curr_val),
            key=f"c_val_{i}_{j}", label_visibility="collapsed"
        )
        if new_val != curr_val:
            cond["value"] = new_val
            save_current_config()


def render_condition_row(cond, i, j):
    """Render a single condition row with all its columns."""
    c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1, 1.5, 0.5])

    with c1:
        new_type = render_condition_indicator(cond, i, j)
    with c2:
        render_condition_period(cond, new_type, i, j)
    with c3:
        render_condition_operator(cond, new_type, i, j)
    with c4:
        render_condition_value(cond, new_type, i, j)
    with c5:
        return st.button("🗑️", key=f"del_c_{i}_{j}")

    return False


def render_group_conditions(group, i):
    """Render all conditions for a group, handling add/remove."""
    st.subheader("Conditions")
    conditions = group.get("conditions", [])
    conds_to_remove = []

    for j, cond in enumerate(conditions):
        should_delete = render_condition_row(cond, i, j)
        if should_delete:
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


def render_group(group, i):
    """Render a single rule group expander. Returns True if the group should be deleted."""
    with st.expander(f"📂 {group.get('name', 'Unnamed')}", expanded=False):
        # Group Name
        new_name = st.text_input("Group Name", value=group.get("name", ""), key=f"g_name_{i}")
        if new_name != group.get("name"):
            group["name"] = new_name
            save_current_config()

        # Logic
        current_logic = group.get("logic", "AND")
        new_logic = st.selectbox(
            "Trigger Logic", ["AND", "OR"],
            index=0 if current_logic == "AND" else 1,
            key=f"g_logic_{i}"
        )
        if new_logic != current_logic:
            group["logic"] = new_logic
            save_current_config()

        st.caption(f"Triggers if **{new_logic}** conditions are met.")

        render_group_conditions(group, i)

        st.divider()
        if st.button("🛑 Delete Group", key=f"del_g_{i}"):
            return True

    return False


def render_alert_rules():
    """Render the alert rules section: add group button and all group expanders."""
    st.header("Alert Rules")

    if st.button("➕ Add New Rule Group"):
        new_group = {
            "name": f"New Group {len(config.get('groups', [])) + 1}",
            "logic": "AND",
            "conditions": []
        }
        config.setdefault("groups", []).append(new_group)
        save_current_config()
        st.rerun()

    groups = config.get("groups", [])
    groups_to_remove = []

    for i, group in enumerate(groups):
        if render_group(group, i):
            groups_to_remove.append(i)

    if groups_to_remove:
        for idx in sorted(groups_to_remove, reverse=True):
            groups.pop(idx)
        save_current_config()
        st.rerun()


def render_sidebar():
    """Top-level sidebar renderer composing all sidebar sections."""
    with st.sidebar:
        st.header("Global Settings")
        render_tickers_input()
        render_webhook_input()
        st.divider()
        render_alert_rules()


# --- Sidebar ---
render_sidebar()


# --- Main Logic ---

def display_results(results_by_group: dict[str, list[dict]]):
    """Display analysis results in the main area and send Discord notifications."""
    if not results_by_group:
        st.info("No tickers matched any of the configured rules.")
        return

    all_alerts_text = []

    for g_name, matches in results_by_group.items():
        st.subheader(f"🔔 {g_name}")
        # Remove internal keys for Streamlit table display
        display_matches = [{k: v for k, v in m.items() if not k.startswith("_")} for m in matches]
        res_df = pd.DataFrame(display_matches)
        st.table(res_df)

        table_text = format_discord_table(matches)
        group_text = f"**{g_name}**:\n{table_text}"
        all_alerts_text.append(group_text)

    # Send Discord notifications
    webhook_url = config.get("webhook_url")
    if not webhook_url:
        st.warning("Notifications skipped (No Webhook URL configured).")
        return

    success_count, total_count, errors = send_batched_notifications(webhook_url, all_alerts_text)

    for error in errors:
        st.error(error)

    if success_count > 0:
        st.toast(f"{success_count} of {total_count} Discord notification(s) sent!", icon="✅")
    if success_count < total_count:
        st.warning(f"Failed to send {total_count - success_count} notification(s).")


if st.button("🚀 Run Analysis", type="primary"):
    ticker_categories = config.get("ticker_categories", {})
    all_tickers = [t for tickers in ticker_categories.values() for t in tickers]
    groups = config.get("groups", [])

    if not all_tickers:
        st.warning("Please add some tickers in the settings.")
    elif not groups:
        st.warning("Please configure at least one rule group.")
    else:
        status = st.status("Analyzing Market Data...", expanded=True)
        status.write("Fetching stock data...")

        try:
            status.write("Evaluating rules...")
            results_by_group = run_analysis(config)
            status.update(label="Analysis Complete!", state="complete", expanded=False)
            display_results(results_by_group)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            import traceback
            st.text(traceback.format_exc())
