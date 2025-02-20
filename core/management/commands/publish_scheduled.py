from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Content

class Command(BaseCommand):
    help = 'Publishes all scheduled content'

    def handle(self, *args, **options):
        now = timezone.now()
        scheduled_content = Content.objects.filter(is_published=False, published_at__lte=now)
        count = scheduled_content.update(is_published=True)
        self.stdout.write(self.style.SUCCESS(f'Successfully published {count} content items'))