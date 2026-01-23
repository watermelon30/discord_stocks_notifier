import requests

def send_discord_message(webhook_url, content):
    """
    Send a message to a Discord Webhook.
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
