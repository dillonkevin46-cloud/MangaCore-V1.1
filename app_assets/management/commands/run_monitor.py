import time
import ping3
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from app_assets.models import Asset, PingRecord
from app_core.models import AppNotification

class Command(BaseCommand):
    help = 'Runs the monitoring engine to ping assets'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Monitoring Engine...'))

        while True:
            self.stdout.write(self.style.SUCCESS(f"\n--- Starting ping cycle at {timezone.now()} ---"))

            assets = Asset.objects.filter(is_monitored=True).exclude(ip_address__isnull=True).exclude(ip_address='')

            if not assets.exists():
                self.stdout.write(self.style.WARNING("No monitored assets found. Sleeping for 60 seconds..."))

            for asset in assets:
                try:
                    self.stdout.write(f"Pinging {asset.name} ({asset.ip_address})...")
                    # Ping the asset (timeout 2 seconds)
                    latency = ping3.ping(asset.ip_address, timeout=2, unit='ms')

                    is_online = False
                    latency_ms = None
                    packet_loss = 0.0

                    if latency is not None and latency is not False:
                        is_online = True
                        latency_ms = latency
                        self.stdout.write(self.style.SUCCESS(f"Status: ONLINE (Latency: {latency_ms:.2f}ms)"))
                    else:
                        is_online = False
                        latency_ms = None
                        packet_loss = 100.0
                        self.stdout.write(self.style.ERROR("Status: OFFLINE"))

                    # Save record
                    PingRecord.objects.create(
                        asset=asset,
                        latency_ms=latency_ms,
                        packet_loss=packet_loss,
                        is_online=is_online
                    )

                    # Alert logic - if an asset fails a ping (was online, now offline)
                    if not is_online:
                        # Get the previous record (excluding the one just created)
                        # We need to be careful not to exclude the one we just created if the logic is flawed
                        # The safest way is to order by -timestamp and take the *second* one.
                        # However, creating one just now means it is the first one.
                        # So we want the one *before* this one.

                        last_record = asset.ping_records.order_by('-timestamp')[1:2]
                        last_record = last_record[0] if last_record else None

                        was_online = True # Default assumption if no history
                        if last_record:
                            was_online = last_record.is_online

                        if was_online:
                            msg = f"ALERT: Asset {asset.name} ({asset.ip_address}) has gone OFFLINE."
                            self.stdout.write(self.style.WARNING(msg))

                            # Create Notification
                            AppNotification.objects.create(
                                message=msg,
                                notification_type='WARNING'
                            )

                            # Send Email
                            if asset.alert_email:
                                try:
                                    send_mail(
                                        subject=f"MagmaCore Monitor Alert: {asset.name} Offline",
                                        message=msg,
                                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@magmacore.local'),
                                        recipient_list=[asset.alert_email],
                                        fail_silently=False
                                    )
                                except Exception as e:
                                    self.stdout.write(self.style.ERROR(f"Failed to send email: {e}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error monitoring {asset.name}: {e}"))

            # Wait 60 seconds
            time.sleep(60)
