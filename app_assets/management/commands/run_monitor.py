import time
import ping3
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from app_assets.models import Asset, PingRecord
from app_core.models import AppNotification

class Command(BaseCommand):
    help = 'Runs the monitoring engine to ping assets'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Monitoring Engine...'))

        while True:
            assets = Asset.objects.filter(is_monitored=True).exclude(ip_address__isnull=True).exclude(ip_address='')

            for asset in assets:
                try:
                    # Ping the asset (timeout 2 seconds)
                    latency = ping3.ping(asset.ip_address, timeout=2, unit='ms')

                    is_online = False
                    latency_ms = None

                    if latency is not None and latency is not False:
                        is_online = True
                        latency_ms = latency
                        packet_loss = 0.0
                    else:
                        is_online = False
                        latency_ms = None
                        packet_loss = 100.0

                    # Save record
                    PingRecord.objects.create(
                        asset=asset,
                        latency_ms=latency_ms,
                        packet_loss=packet_loss,
                        is_online=is_online
                    )

                    # Alert logic
                    # Get the previous record to see if state changed
                    last_record = asset.ping_records.order_by('-timestamp').exclude(pk=PingRecord.objects.latest('timestamp').pk).first()

                    # If it was online and now offline
                    # Or if we just want to alert on every failure (can be noisy, stick to state change or failure)
                    # Requirement: "If an asset fails a ping (was online, now offline)"

                    # If current is offline
                    if not is_online:
                        # Check if it was previously online or if this is the first check
                        was_online = True # Default assumption if no history, maybe? Or false.
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
                                        fail_silently=True
                                    )
                                except Exception as e:
                                    self.stdout.write(self.style.ERROR(f"Failed to send email: {e}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error monitoring {asset.name}: {e}"))

            # Wait 60 seconds
            time.sleep(60)
