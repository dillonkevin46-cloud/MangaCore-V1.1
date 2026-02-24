import requests
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import close_old_connections
from django.contrib.auth import get_user_model
from app_tickets.models import Ticket

User = get_user_model()

class Command(BaseCommand):
    help = 'Check for new emails via Microsoft Graph API and create tickets'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Email-to-Ticket Engine (MS Graph API)..."))

        tenant_id = getattr(settings, 'MS_GRAPH_TENANT_ID', None)
        client_id = getattr(settings, 'MS_GRAPH_CLIENT_ID', None)
        client_secret = getattr(settings, 'MS_GRAPH_CLIENT_SECRET', None)
        mailbox = getattr(settings, 'MS_GRAPH_MAILBOX', None)

        if not all([tenant_id, client_id, client_secret, mailbox]):
            self.stdout.write(self.style.ERROR("Missing MS Graph API settings in settings.py"))
            return

        while True:
            # Prevent stale DB connections
            close_old_connections()

            try:
                # Step A: Get Access Token
                token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
                token_data = {
                    'client_id': client_id,
                    'scope': 'https://graph.microsoft.com/.default',
                    'client_secret': client_secret,
                    'grant_type': 'client_credentials'
                }

                try:
                    token_response = requests.post(token_url, data=token_data)
                    token_response.raise_for_status()
                    access_token = token_response.json().get('access_token')

                    if not access_token:
                        self.stdout.write(self.style.ERROR("Failed to retrieve access token."))
                        time.sleep(60)
                        continue

                except requests.RequestException as e:
                     self.stdout.write(self.style.ERROR(f"Token Request Failed: {e}"))
                     time.sleep(60)
                     continue

                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }

                # Step B: Fetch Unread Emails
                messages_url = f"https://graph.microsoft.com/v1.0/users/{mailbox}/mailFolders/inbox/messages?$filter=isRead eq false"

                try:
                    messages_response = requests.get(messages_url, headers=headers)
                    messages_response.raise_for_status()
                    emails = messages_response.json().get('value', [])
                except requests.RequestException as e:
                    self.stdout.write(self.style.ERROR(f"Failed to fetch messages: {e}"))
                    time.sleep(60)
                    continue

                if not emails:
                    self.stdout.write(self.style.SUCCESS("No new emails found."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Found {len(emails)} new emails."))

                # Step C: Process and Create Tickets
                for email_data in emails:
                    email_id = email_data.get('id')
                    subject = email_data.get('subject', 'No Subject')

                    # Try to get body content, fallback to bodyPreview
                    body_content = email_data.get('body', {}).get('content', '')
                    body_preview = email_data.get('bodyPreview', '')
                    description = body_content if body_content else body_preview

                    sender_email = email_data.get('from', {}).get('emailAddress', {}).get('address', 'unknown@example.com')

                    self.stdout.write(f"Processing email: {subject} from {sender_email}")

                    # Find or Create User (Simple logic to assign creator)
                    # If user exists, assign them. If not, assign to a default 'system' user or create one?
                    # The prompt said "Create a Ticket object (e.g., title=subject, description=body, status='OPEN')."
                    # But the Ticket model requires a 'creator'.
                    # I will replicate the previous logic: Find or Create User based on sender email.

                    user, created = User.objects.get_or_create(email=sender_email)
                    if created:
                        user.username = sender_email.split('@')[0]
                        # Ensure uniqueness
                        if User.objects.filter(username=user.username).exists():
                             import random
                             user.username = f"{user.username}_{random.randint(1000, 9999)}"
                        user.set_password(User.objects.make_random_password())
                        user.save()
                        self.stdout.write(self.style.SUCCESS(f"Created new user: {user.username}"))

                    # Create Ticket
                    try:
                        Ticket.objects.create(
                            title=subject[:200], # Truncate to max_length
                            description=description,
                            creator=user,
                            status=Ticket.Status.OPEN,
                            priority=Ticket.Priority.MEDIUM
                        )
                        self.stdout.write(self.style.SUCCESS(f"Ticket created for: {subject}"))

                        # Step D: Mark as Read
                        patch_url = f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{email_id}"
                        patch_data = {'isRead': True}
                        requests.patch(patch_url, headers=headers, json=patch_data)

                    except Exception as e:
                         self.stdout.write(self.style.ERROR(f"Error creating ticket: {e}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Unexpected error in main loop: {e}"))

            # Sleep for 60 seconds
            self.stdout.write("Sleeping for 60 seconds...")
            time.sleep(60)
