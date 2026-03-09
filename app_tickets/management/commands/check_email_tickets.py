import requests
import time
import base64
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import close_old_connections
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from app_tickets.models import Ticket, TicketAttachment
from app_tickets.utils import get_graph_token

User = get_user_model()

class Command(BaseCommand):
    help = 'Check for new emails via Microsoft Graph API and create tickets'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Email-to-Ticket Engine (MS Graph API)..."))

        mailbox = getattr(settings, 'MS_GRAPH_MAILBOX', None)

        if not mailbox:
            self.stdout.write(self.style.ERROR("Missing MS_GRAPH_MAILBOX setting in settings.py"))
            return

        while True:
            # Prevent stale DB connections
            close_old_connections()

            try:
                # Get Token
                access_token = get_graph_token()

                if not access_token:
                    self.stdout.write(self.style.ERROR("Failed to retrieve access token."))
                    time.sleep(60)
                    continue

                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }

                # Fetch Unread Emails
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

                # Process and Create Tickets
                for email_data in emails:
                    email_id = email_data.get('id')
                    subject = email_data.get('subject', 'No Subject')
                    has_attachments = email_data.get('hasAttachments', False)

                    # Try to get body content, fallback to bodyPreview
                    body_content = email_data.get('body', {}).get('content', '')
                    body_preview = email_data.get('bodyPreview', '')
                    description = body_content if body_content else body_preview

                    sender_email = email_data.get('from', {}).get('emailAddress', {}).get('address')
                    sender_email = sender_email if sender_email else "unknown@magmacore.local"

                    self.stdout.write(f"Processing email: {subject} from {sender_email}")

                    # Find or Create User
                    user, created = User.objects.get_or_create(email=sender_email)
                    if created:
                        username_base = sender_email.split('@')[0] if '@' in sender_email else 'unknown_user'
                        if not username_base:
                            username_base = f"user_{get_random_string(6)}"

                        user.username = username_base
                        # Ensure uniqueness
                        if User.objects.filter(username=user.username).exists():
                             user.username = f"{username_base}_{get_random_string(4)}"
                        user.set_password(User.objects.make_random_password())
                        user.save()
                        self.stdout.write(self.style.SUCCESS(f"Created new user: {user.username}"))

                    # Create Ticket
                    try:
                        ticket = Ticket.objects.create(
                            title=subject[:200], # Truncate to max_length
                            description=description,
                            creator=user,
                            status=Ticket.Status.OPEN,
                            priority=Ticket.Priority.MEDIUM
                        )
                        self.stdout.write(self.style.SUCCESS(f"Ticket created for: {subject}"))

                        # Fetch and Save Attachments
                        if has_attachments:
                            attachments_url = f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{email_id}/attachments"
                            try:
                                att_response = requests.get(attachments_url, headers=headers)
                                att_response.raise_for_status()
                                attachments = att_response.json().get('value', [])

                                for att in attachments:
                                    if 'contentBytes' in att:
                                        raw_name = att.get('name')
                                        if not raw_name:
                                            filename = f"image_{get_random_string(6)}.png"
                                        else:
                                            filename = raw_name

                                        decoded_bytes = base64.b64decode(att['contentBytes'])
                                        TicketAttachment.objects.create(
                                            ticket=ticket,
                                            file=ContentFile(decoded_bytes, name=filename),
                                            filename=filename
                                        )
                                        self.stdout.write(self.style.SUCCESS(f"Saved attachment: {filename}"))
                            except requests.RequestException as e:
                                self.stdout.write(self.style.ERROR(f"Failed to fetch attachments for {email_id}: {e}"))
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f"Error saving attachment: {e}"))

                        # Mark as Read
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
