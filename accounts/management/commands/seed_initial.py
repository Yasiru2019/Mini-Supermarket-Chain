from django.core.management.base import BaseCommand

from outlets.models import Outlet


class Command(BaseCommand):
    help = 'Seeds a default outlet for local development (Step 1 checkpoint).'

    def handle(self, *args, **options):
        outlet, created = Outlet.objects.get_or_create(
            name='Main Outlet',
            defaults={
                'address': 'TBD',
                'phone': '',
                'gst_number': '',
                'timezone': 'Pacific/Port_Moresby',
                'is_active': True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created outlet: {outlet.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Outlet already exists: {outlet.name}'))
