import requests
from django.conf import settings

def get_graph_token():
    token_url = f"https://login.microsoftonline.com/{settings.MS_GRAPH_TENANT_ID}/oauth2/v2.0/token"
    token_data = {
        'client_id': settings.MS_GRAPH_CLIENT_ID,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': settings.MS_GRAPH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    token_r = requests.post(token_url, data=token_data)
    token_r.raise_for_status()
    return token_r.json().get('access_token')

def send_graph_email(to_email, subject, body_text):
    token = get_graph_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body_text
            },
            "toRecipients": [
                {"emailAddress": {"address": to_email}}
            ]
        }
    }
    url = f"https://graph.microsoft.com/v1.0/users/{settings.MS_GRAPH_MAILBOX}/sendMail"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()