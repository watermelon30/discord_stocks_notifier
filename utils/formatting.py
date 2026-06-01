def format_discord_table(matches: list[dict]) -> str:
    """
    Generates a monospaced ASCII table for Discord.
    matches: list of dicts containing ticker and indicator stats.
    """
    if not matches:
        return "No matches found."

    # Define Column Order: Ticker first, then Price, then RSI/RCI, then EMAs, then Days>EMA
    all_keys = set().union(*(m.keys() for m in matches))
    ema_cols = sorted([k for k in all_keys if "EMA" in k and not k.startswith("Days")])
    days_cols = sorted([k for k in all_keys if k.startswith("Days")])

    # Static priority headers
    headers = ["Ticker", "Price"]
    if "RSI" in all_keys:
        headers.append("RSI")
    if "RCI" in all_keys:
        headers.append("RCI")
    headers.extend(ema_cols)
    headers.extend(days_cols)

    # Calculate column widths based on longest string in header or data
    widths = {h: len(h) for h in headers}
    for m in matches:
        for h in headers:
            val = str(m.get(h, "-"))
            widths[h] = max(widths[h], len(val))

    def make_row(row_data):
        return "| " + " | ".join(
            str(row_data.get(h, "-")).ljust(widths[h]) for h in headers
        ) + " |"

    def make_separator():
        return "+" + "+".join("-" * (widths[h] + 2) for h in headers) + "+"

    # Construct table
    table_lines = [make_separator(), make_row({h: h for h in headers}), make_separator()]
    for m in matches:
        table_lines.append(make_row(m))
    table_lines.append(make_separator())

    return "```\n" + "\n".join(table_lines) + "\n```"
