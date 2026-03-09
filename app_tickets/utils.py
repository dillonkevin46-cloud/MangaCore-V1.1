import requests
from django.conf import settings

def get_graph_token():
    """
    Requests an access token from Microsoft Graph API using client credentials.
    """
    tenant_id = getattr(settings, 'MS_GRAPH_TENANT_ID', None)
    client_id = getattr(settings, 'MS_GRAPH_CLIENT_ID', None)
    client_secret = getattr(settings, 'MS_GRAPH_CLIENT_SECRET', None)

    if not all([tenant_id, client_id, client_secret]):
        print("Missing MS Graph API token settings.")
        return None

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'client_id': client_id,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.RequestException as e:
        print(f"Failed to get MS Graph token: {e}")
        return None

def send_graph_email(to_email, subject, body_text):
    """
    Sends an email using Microsoft Graph API.
    """
    access_token = get_graph_token()
    if not access_token:
        print("Failed to get token for sending email.")
        return False

    mailbox = getattr(settings, 'MS_GRAPH_MAILBOX', None)
    if not mailbox:
        print("Missing MS_GRAPH_MAILBOX setting.")
        return False

    send_url = f"https://graph.microsoft.com/v1.0/users/{mailbox}/sendMail"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    email_payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body_text
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email
                    }
                }
            ]
        }
    }

    try:
        response = requests.post(send_url, headers=headers, json=email_payload)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Failed to send email via MS Graph: {e}")
        if response.text:
            print(response.text)
        return False
