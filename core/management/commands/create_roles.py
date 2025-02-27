from django.core.management.base import BaseCommand
from core.models import Role

class Command(BaseCommand):
    help = 'Create initial roles'

    def handle(self, *args, **options):
        roles = ['Admin', 'Editor', 'Author', 'Viewer']
        for role_name in roles:
            Role.objects.get_or_create(name=role_name)
        self.stdout.write(self.style.SUCCESS('Roles created successfully'))