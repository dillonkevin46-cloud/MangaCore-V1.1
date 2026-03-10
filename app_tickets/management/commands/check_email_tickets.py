import base64
import requests
import time
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.db import close_old_connections

# Dynamically load the models
from django.apps import apps
from app_tickets.models import Ticket, TicketAttachment

User = get_user_model()

class Command(BaseCommand):
    help = 'Check for new emails and process Tickets/Replies via MS Graph API'

    def handle(self, *args, **options):
        try:
            CommentModel = apps.get_model('app_tickets', 'TicketComment')
        except LookupError:
            try:
                CommentModel = apps.get_model('app_tickets', 'Comment')
            except LookupError:
                CommentModel = None

        tenant_id = getattr(settings, 'MS_GRAPH_TENANT_ID', None)
        client_id = getattr(settings, 'MS_GRAPH_CLIENT_ID', None)
        client_secret = getattr(settings, 'MS_GRAPH_CLIENT_SECRET', None)
        mailbox = getattr(settings, 'MS_GRAPH_MAILBOX', None)

        if not all([tenant_id, client_id, client_secret, mailbox]):
            self.stdout.write(self.style.ERROR("MS Graph API settings are missing."))
            return

        self.stdout.write(self.style.SUCCESS("Starting Aggressive Email Engine (Regex CID & Threading)..."))

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

                        body = ""
                        if msg.get('body') and msg['body'].get('content'):
                            body = msg['body']['content']
                        else:
                            body = msg.get('bodyPreview', '')

                        # 4. THREADING LOGIC
                        ticket = None
                        is_reply = False
                        
                        match = re.search(r'#(\d+)', subject)
                        if match:
                            try:
                                ticket = Ticket.objects.get(id=match.group(1))
                                is_reply = True
                            except Ticket.DoesNotExist:
                                pass 

                        target_obj = None
                        if is_reply and CommentModel:
                            comment_kwargs = {'ticket': ticket}
                            if hasattr(CommentModel, 'user'): comment_kwargs['user'] = user
                            else: comment_kwargs['author'] = user
                            
                            if hasattr(CommentModel, 'comment'): comment_kwargs['comment'] = body
                            else: comment_kwargs['content'] = body
                            
                            if hasattr(CommentModel, 'is_internal'): comment_kwargs['is_internal'] = False
                            elif hasattr(CommentModel, 'is_public'): comment_kwargs['is_public'] = True
                            
                            target_obj = CommentModel.objects.create(**comment_kwargs)
                            self.stdout.write(self.style.SUCCESS(f"Added reply to existing Ticket #{ticket.id}"))
                        else:
                            ticket = Ticket.objects.create(title=subject, description=body, creator=user, status=Ticket.Status.OPEN)
                            target_obj = ticket
                            self.stdout.write(self.style.SUCCESS(f"Created NEW Ticket #{ticket.id}"))

                        # 5. AGGRESSIVE ATTACHMENT FETCH (Ignore hasAttachments flag)
                        att_url = f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{msg_id}/attachments"
                        att_r = requests.get(att_url, headers=headers)
                        
                        if att_r.status_code == 200:
                            for att in att_r.json().get('value', []):
                                content_bytes = att.get('contentBytes', '')
                                if content_bytes:
                                    content_bytes += "=" * ((4 - len(content_bytes) % 4) % 4)
                                    decoded_bytes = base64.b64decode(content_bytes)
                                    
                                    filename = att.get('name') or f"image_{get_random_string(6)}.png"
                                    attachment = TicketAttachment.objects.create(ticket=ticket, file=ContentFile(decoded_bytes, name=filename), filename=filename)
                                    self.stdout.write(self.style.SUCCESS(f"Saved attachment: {filename}"))
                                    
                                    # Regex CID Replacement
                                    cid = att.get('contentId')
                                    if cid:
                                        clean_cid = cid.strip('<>') 
                                        short_cid = clean_cid.split('@')[0] if '@' in clean_cid else clean_cid
                                        
                                        def replace_cid_in_text(text, full_c, short_c, url):
                                            if not text: return text
                                            # Case insensitive regex replace for both full and short versions of the CID
                                            text = re.sub(re.escape(f"cid:{full_c}"), url, text, flags=re.IGNORECASE)
                                            text = re.sub(re.escape(f"cid:{short_c}"), url, text, flags=re.IGNORECASE)
                                            return text
                                        
                                        if hasattr(target_obj, 'description'):
                                            target_obj.description = replace_cid_in_text(target_obj.description, clean_cid, short_cid, attachment.file.url)
                                        elif hasattr(target_obj, 'comment'):
                                            target_obj.comment = replace_cid_in_text(target_obj.comment, clean_cid, short_cid, attachment.file.url)
                                        elif hasattr(target_obj, 'content'):
                                            target_obj.content = replace_cid_in_text(target_obj.content, clean_cid, short_cid, attachment.file.url)
                                        
                                        target_obj.save()

                        # 6. Mark Email as Read
                        requests.patch(f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{msg_id}", headers=headers, json={'isRead': True})

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing email: {e}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Graph API Connection Error: {e}"))
                
            time.sleep(60)