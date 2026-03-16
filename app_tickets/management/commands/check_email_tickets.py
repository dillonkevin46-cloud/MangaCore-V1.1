import base64
import requests
import time
import re
import html  # <--- NEW: Added to fix Exchange escaping
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.db import close_old_connections

# EXPLICIT IMPORTS 
from app_tickets.models import Ticket, TicketAttachment, TicketComment
from app_tickets.utils import send_graph_email

User = get_user_model()

class Command(BaseCommand):
    help = 'Check for new emails and process Tickets/Replies via MS Graph API'

    def handle(self, *args, **options):
        tenant_id = getattr(settings, 'MS_GRAPH_TENANT_ID', None)
        client_id = getattr(settings, 'MS_GRAPH_CLIENT_ID', None)
        client_secret = getattr(settings, 'MS_GRAPH_CLIENT_SECRET', None)
        mailbox = getattr(settings, 'MS_GRAPH_MAILBOX', None)

        if not all([tenant_id, client_id, client_secret, mailbox]):
            self.stdout.write(self.style.ERROR("MS Graph API settings are missing."))
            return

        self.stdout.write(self.style.SUCCESS("Starting Engine (Impenetrable HTML Machete)..."))

        while True:
            close_old_connections()
            try:
                # 1. Get Access Token
                token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
                token_r = requests.post(token_url, data={
                    'client_id': client_id,
                    'scope': 'https://graph.microsoft.com/.default',
                    'client_secret': client_secret,
                    'grant_type': 'client_credentials'
                })
                token_r.raise_for_status()
                access_token = token_r.json().get('access_token')
                headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

                # 2. Fetch Unread Emails
                messages_url = f"https://graph.microsoft.com/v1.0/users/{mailbox}/mailFolders/inbox/messages?$filter=isRead eq false"
                messages_r = requests.get(messages_url, headers=headers)
                messages_r.raise_for_status()
                messages_data = messages_r.json().get('value', [])

                for msg in messages_data:
                    try:
                        msg_id = msg.get('id')
                        subject = msg.get('subject', 'No Subject')
                        
                        sender_email = 'unknown@magmacore.local'
                        if msg.get('sender') and msg['sender'].get('emailAddress'):
                            sender_email = msg['sender']['emailAddress'].get('address', sender_email)

                        # 3. Secure User Creation
                        user = User.objects.filter(email=sender_email).first()
                        if not user:
                            username_base = sender_email.split('@')[0] if '@' in sender_email else 'user'
                            username = username_base
                            counter = 1
                            while User.objects.filter(username=username).exists():
                                username = f"{username_base}_{counter}"
                                counter += 1
                            user = User.objects.create_user(username=username, email=sender_email, password=get_random_string(12))

                        # ----------------------------------------------------
                        # PHASE 33: IMPENETRABLE HTML CLEANER
                        # ----------------------------------------------------
                        body = ""
                        if msg.get('body') and msg['body'].get('content'):
                            raw_body = msg['body']['content']
                            
                            # Safely unescape weird Microsoft HTML formatting
                            raw_body = html.unescape(raw_body)
                            
                            # Annihilate the Head, Style, HTML Comments, HTML, Body, and Meta tags
                            raw_body = re.compile(r'<head[^>]*>.*?</head>', re.IGNORECASE | re.DOTALL).sub('', raw_body)
                            raw_body = re.compile(r'<style[^>]*>.*?</style>', re.IGNORECASE | re.DOTALL).sub('', raw_body)
                            raw_body = re.compile(r'', re.IGNORECASE | re.DOTALL).sub('', raw_body)
                            raw_body = re.compile(r'</?html[^>]*>', re.IGNORECASE).sub('', raw_body)
                            raw_body = re.compile(r'</?body[^>]*>', re.IGNORECASE).sub('', raw_body)
                            raw_body = re.compile(r'<meta[^>]*>', re.IGNORECASE).sub('', raw_body)
                            
                            # Physically sever the string at the signature/reply line
                            cutoffs = [
                                r'<div[^>]*id="Signature"',
                                r'<div[^>]*class="Signature"',
                                r'<div[^>]*id="appendonsend"',
                                r'<div[^>]*id="divRplyFwdMsg"',
                                r'<hr[^>]*tabindex="-1"',
                                r'<div[^>]*class="gmail_quote"',
                                r'<blockquote',
                                r'<div[^>]*class="yahoo_quoted"'
                            ]
                            
                            for cutoff in cutoffs:
                                raw_body = re.compile(cutoff, re.IGNORECASE).split(raw_body)[0]
                                
                            body = raw_body.strip()
                        else:
                            body = msg.get('bodyPreview', '')
                        # ----------------------------------------------------

                        # 4. THREADING LOGIC 
                        ticket = None
                        is_reply = False
                        target_obj = None
                        
                        self.stdout.write(f"\n--- Processing Email: {subject} ---")
                        match = re.search(r'#(\d+)', subject)
                        
                        if match:
                            found_id = match.group(1)
                            self.stdout.write(f"Regex found Ticket ID #{found_id} in subject.")
                            try:
                                ticket = Ticket.objects.get(id=found_id)
                                is_reply = True
                                self.stdout.write(self.style.SUCCESS(f"Successfully matched with database Ticket #{ticket.id}"))
                            except Ticket.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f"Ticket #{found_id} does NOT exist. Treating as new ticket."))

                        if is_reply:
                            target_obj = TicketComment.objects.create(
                                ticket=ticket,
                                user=user,
                                comment=body,
                                is_internal=False
                            )
                            self.stdout.write(self.style.SUCCESS(f"Added clean reply to Ticket #{ticket.id}"))
                        else:
                            ticket = Ticket.objects.create(title=subject, description=body, creator=user, status=Ticket.Status.OPEN)
                            target_obj = ticket
                            self.stdout.write(self.style.SUCCESS(f"Created brand NEW Ticket #{ticket.id}"))
                            
                            try:
                                auto_reply_text = f"Thank you for contacting IT Support.\n\nYour ticket has been successfully logged. Please reply directly to this email to communicate with our technicians.\n\n"
                                send_graph_email(sender_email, f"RE: #{ticket.id} - {subject}", auto_reply_text)
                                self.stdout.write(self.style.SUCCESS(f"Sent Auto-Responder to {sender_email}"))
                            except Exception as email_err:
                                self.stdout.write(self.style.ERROR(f"Failed to send Auto-Responder: {email_err}"))

                        # 5. ANTI-DUPLICATION ATTACHMENT FETCH
                        att_url = f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{msg_id}/attachments"
                        att_r = requests.get(att_url, headers=headers)
                        
                        if att_r.status_code == 200:
                            for att in att_r.json().get('value', []):
                                content_bytes = att.get('contentBytes', '')
                                if content_bytes:
                                    content_bytes += "=" * ((4 - len(content_bytes) % 4) % 4)
                                    decoded_bytes = base64.b64decode(content_bytes)
                                    
                                    filename = att.get('name') or f"image_{get_random_string(6)}.png"
                                    file_size = len(decoded_bytes)
                                    
                                    # CHECK FOR DUPLICATES ON THIS TICKET
                                    is_duplicate = False
                                    attachment = None
                                    
                                    for existing_att in ticket.attachments.all():
                                        try:
                                            # If exact filename and exact size already exist, it's a duplicate signature image!
                                            if existing_att.filename == filename and existing_att.file.size == file_size:
                                                is_duplicate = True
                                                attachment = existing_att
                                                break
                                        except Exception:
                                            pass
                                            
                                    if not is_duplicate:
                                        attachment = TicketAttachment.objects.create(ticket=ticket, file=ContentFile(decoded_bytes, name=filename), filename=filename)
                                        self.stdout.write(self.style.SUCCESS(f"Saved NEW attachment: {filename}"))
                                    else:
                                        self.stdout.write(f"Skipped duplicate signature image: {filename}")
                                    
                                    # CID MAPPING (Works for both new and duplicate images)
                                    cid = att.get('contentId')
                                    if cid and attachment:
                                        clean_cid = cid.strip('<>') 
                                        short_cid = clean_cid.split('@')[0] if '@' in clean_cid else clean_cid
                                        
                                        def replace_cid_in_text(text, full_c, short_c, url):
                                            if not text: return text
                                            text = re.sub(re.escape(f"cid:{full_c}"), url, text, flags=re.IGNORECASE)
                                            text = re.sub(re.escape(f"cid:{short_c}"), url, text, flags=re.IGNORECASE)
                                            return text
                                        
                                        if is_reply:
                                            target_obj.comment = replace_cid_in_text(target_obj.comment, clean_cid, short_cid, attachment.file.url)
                                        else:
                                            target_obj.description = replace_cid_in_text(target_obj.description, clean_cid, short_cid, attachment.file.url)
                                        
                                        target_obj.save()

                        # 6. Mark Email as Read
                        requests.patch(f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{msg_id}", headers=headers, json={'isRead': True})

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing individual email: {e}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Graph API Error: {e}"))
                
            time.sleep(60)