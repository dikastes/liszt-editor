from django.conf import settings
from django.core.management.base import BaseCommand
from dmrism.models import Library

class Command(BaseCommand):
    help = "Sepcify a file to import manifestations from."

    def handle(self, *args, **options):
        for empty_library_name in settings.EDWOCA_EMPTY_LIBRARIES:
            Library.objects.create(name = empty_library_name)
