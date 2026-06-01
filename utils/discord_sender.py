import requests


def send_discord_message(webhook_url: str, content: str) -> tuple[bool, str]:
    """
    Send a single message to a Discord Webhook.
    Returns (success, message).
    """
    if not webhook_url:
        return False, "No Webhook URL provided"

    data = {"content": content}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            return True, "Message sent successfully"
        else:
            return False, f"Failed to send message: {response.status_code} - {response.text}"
    except Exception as e:
        return False, str(e)


DISCORD_CHAR_LIMIT = 2000


def batch_discord_messages(all_alerts_text: list[str], header: str = "**Stock Alerts Triggered**") -> list[str]:
    """
    Batch alert texts into Discord-safe messages that respect the character limit.
    Returns a list of ready-to-send message strings (with header and pagination).
    """
    if not all_alerts_text:
        return []

    messages_to_send = []
    current_parts = []
    # Reserve space for header, page numbers like (1/2), and newlines
    current_length = len(header) + 20

    for group_alert in all_alerts_text:
        alert_len = len(group_alert) + 2  # for \n\n separator

        if current_parts and current_length + alert_len > DISCORD_CHAR_LIMIT:
            messages_to_send.append("\n\n".join(current_parts))
            current_parts = []
            current_length = len(header) + 20

        current_parts.append(group_alert)
        current_length += alert_len

    if current_parts:
        messages_to_send.append("\n\n".join(current_parts))

    # Attach headers with pagination
    num_messages = len(messages_to_send)
    final_messages = []
    for i, body in enumerate(messages_to_send):
        final_header = header
        if num_messages > 1:
            final_header += f" ({i + 1}/{num_messages})"
        final_messages.append(f"{final_header}\n\n{body}")

    return final_messages


def send_batched_notifications(webhook_url: str, all_alerts_text: list[str]) -> tuple[int, int, list[str]]:
    """
    Batch and send all alert texts to Discord.
    Returns (success_count, total_count, error_messages).
    """
    messages = batch_discord_messages(all_alerts_text)
    if not messages:
        return 0, 0, []

    success_count = 0
    errors = []

    for i, full_msg in enumerate(messages):
        if len(full_msg) > DISCORD_CHAR_LIMIT:
            errors.append(
                f"Message {i + 1}/{len(messages)} is too long ({len(full_msg)} chars) "
                f"and could not be sent. This can happen if a single group's alert is too large."
            )
            continue

        success, resp = send_discord_message(webhook_url, full_msg)
        if success:
            success_count += 1
        else:
            errors.append(f"Discord Error on message {i + 1}/{len(messages)}: {resp}")

    return success_count, len(messages), errors
