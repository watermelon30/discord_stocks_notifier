def format_discord_table(matches: list[dict]) -> str:
    """
    Generates a monospaced ASCII table for Discord with category grouping.
    matches: list of dicts containing ticker and indicator stats.
    Each dict may contain a '_category' key for grouping.
    """
    if not matches:
        return "No matches found."

    # Define Column Order: Ticker first, then Price, then RSI/RCI, then EMAs, then Days>EMA
    # Exclude internal keys (prefixed with _) from headers
    all_keys = set().union(*(m.keys() for m in matches))
    all_keys = {k for k in all_keys if not k.startswith("_")}
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

    total_width = sum(widths[h] + 3 for h in headers) + 1  # +3 for " | ", +1 for leading "|"

    def make_row(row_data):
        return "| " + " | ".join(
            str(row_data.get(h, "-")).ljust(widths[h]) for h in headers
        ) + " |"

    def make_separator():
        return "+" + "+".join("-" * (widths[h] + 2) for h in headers) + "+"

    def make_category_row(category_name):
        """Create a centered category label row spanning the full table width."""
        inner_width = total_width - 2  # exclude outer | characters
        label = category_name.center(inner_width)
        return "|" + label + "|"

    # Group matches by category, preserving order of first appearance
    has_categories = any(m.get("_category") for m in matches)

    if has_categories:
        # Collect categories in order of first appearance
        seen_categories = []
        categorized: dict[str, list[dict]] = {}
        for m in matches:
            cat = m.get("_category", "Other")
            if cat not in categorized:
                seen_categories.append(cat)
                categorized[cat] = []
            categorized[cat].append(m)

        # Build table with category headers
        table_lines = [make_separator(), make_row({h: h for h in headers}), make_separator()]
        for cat in seen_categories:
            table_lines.append(make_category_row(cat))
            for m in categorized[cat]:
                table_lines.append(make_row(m))
        table_lines.append(make_separator())
    else:
        # No categories — flat table
        table_lines = [make_separator(), make_row({h: h for h in headers}), make_separator()]
        for m in matches:
            table_lines.append(make_row(m))
        table_lines.append(make_separator())

    return "```\n" + "\n".join(table_lines) + "\n```"
