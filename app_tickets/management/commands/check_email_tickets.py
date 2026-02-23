import imaplib
import email
from email.header import decode_header
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from app_tickets.models import Ticket
from django.utils.crypto import get_random_string

User = get_user_model()

class Command(BaseCommand):
    help = 'Check for new emails and create tickets'

    def handle(self, *args, **options):
        imap_server = getattr(settings, 'IMAP_SERVER', None)
        username = getattr(settings, 'IMAP_USERNAME', None)
        password = getattr(settings, 'IMAP_PASSWORD', None)

        if not all([imap_server, username, password]):
            self.stdout.write(self.style.ERROR("IMAP settings are missing in settings.py"))
            return

        try:
            self.stdout.write(f"Connecting to {imap_server}...")
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(username, password)
            mail.select("inbox")

            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()

            if not email_ids:
                self.stdout.write(self.style.SUCCESS("No new emails found."))
                return

            self.stdout.write(self.style.SUCCESS(f"Found {len(email_ids)} new emails. Processing..."))

            for email_id in email_ids:
                try:
                    res, msg_data = mail.fetch(email_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])

                            subject_header = msg["Subject"]
                            if subject_header:
                                decoded_list = decode_header(subject_header)
                                subject = ""
                                for s, encoding in decoded_list:
                                    if isinstance(s, bytes):
                                        subject += s.decode(encoding if encoding else "utf-8")
                                    else:
                                        subject += s
                            else:
                                subject = "No Subject"

                            from_header = msg.get("From")
                            sender_email = email.utils.parseaddr(from_header)[1]

                            self.stdout.write(f"Processing email from {sender_email}: {subject}")

                            # Find or Create User
                            try:
                                user = User.objects.get(email=sender_email)
                            except User.DoesNotExist:
                                username_base = sender_email.split('@')[0]
                                username = username_base
                                counter = 1
                                while User.objects.filter(username=username).exists():
                                    username = f"{username_base}_{counter}"
                                    counter += 1

                                user = User.objects.create_user(
                                    username=username,
                                    email=sender_email,
                                    password=get_random_string(12)
                                )
                                self.stdout.write(self.style.SUCCESS(f"Created new user: {user.username}"))
                            except User.MultipleObjectsReturned:
                                # Fallback if multiple users share email (shouldn't happen ideally)
                                user = User.objects.filter(email=sender_email).first()

                            # Extract Body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition"))

                                    if content_type == "text/plain" and "attachment" not in content_disposition:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            charset = part.get_content_charset() or 'utf-8'
                                            body = payload.decode(charset, errors='replace')
                                        break
                            else:
                                payload = msg.get_payload(decode=True)
                                if payload:
                                    charset = msg.get_content_charset() or 'utf-8'
                                    body = payload.decode(charset, errors='replace')

                            # Create Ticket
                            ticket = Ticket.objects.create(
                                title=subject,
                                description=body,
                                creator=user,
                                status=Ticket.Status.OPEN,
                                priority=Ticket.Priority.MEDIUM
                            )

                            # Handle Attachments
                            for part in msg.walk():
                                if part.get_content_maintype() == 'multipart':
                                    continue
                                if part.get('Content-Disposition') is None:
                                    continue

                                filename = part.get_filename()
                                if filename:
                                    filename_parts = decode_header(filename)
                                    decoded_filename = ""
                                    for f, encoding in filename_parts:
                                        if isinstance(f, bytes):
                                            decoded_filename += f.decode(encoding if encoding else 'utf-8')
                                        else:
                                            decoded_filename += f
                                    filename = decoded_filename

                                    content = part.get_payload(decode=True)
                                    if content:
                                        # Save attachment
                                        ticket.attachment.save(filename, ContentFile(content))
                                        self.stdout.write(f"Saved attachment: {filename}")
                                        break # Limit to one per ticket based on current model

                            self.stdout.write(self.style.SUCCESS(f"Ticket #{ticket.id} created."))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing email {email_id}: {e}"))

            mail.close()
            mail.logout()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"IMAP Connection Error: {e}"))
