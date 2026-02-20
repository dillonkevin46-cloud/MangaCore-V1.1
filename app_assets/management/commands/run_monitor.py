import time
import ping3
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import close_old_connections
from app_assets.models import Asset, PingRecord

class Command(BaseCommand):
    help = 'Runs the monitoring engine to ping assets'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Monitoring Engine...'))

        while True:
            # CRITICAL: Prevent stale connections
            close_old_connections()

            self.stdout.write(self.style.SUCCESS(f"\n--- Starting ping cycle at {timezone.now()} ---"))

            # Fetch all assets
            all_assets = Asset.objects.all()

            # Pure Python filtering
            monitored_assets = [
                a for a in all_assets
                if a.is_monitored is True and a.ip_address and str(a.ip_address).strip() != ''
            ]

            if not monitored_assets:
                self.stdout.write(self.style.WARNING("No valid devices met the filter criteria."))

            for asset in monitored_assets:
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

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error monitoring {asset.name}: {e}"))

            # Sleep for 10 seconds
            time.sleep(10)
