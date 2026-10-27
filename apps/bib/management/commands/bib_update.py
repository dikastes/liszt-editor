from bib.tasks import update_zotero_items
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    """ Imports items from zotero-bib """

    help = "Updates zotero-bib"

    def handle(self, *args, **options):
        self.stdout.write("Sending import task to celery")

        task = update_zotero_items.delay()

        self.stdout.write(self.style.SUCCESS(f"Task sent to celery. ID: {task.id}"))
