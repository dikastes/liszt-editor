import logging
import datetime
from celery import shared_task
from django.conf import settings
from .zot_utils import items_to_dict, create_zotitem
from .models import ZotItem, library_id

logger = logging.getLogger(__name__)

@shared_task
def update_zotero_items():
    library_id = settings.Z_ID
    library_type = settings.Z_LIBRARY_TYPE
    api_key = settings.Z_API_KEY

    limit = None
    try:
        first_object = ZotItem.objects.first()
        since = first_object.zot_version
    except ZotItem.DoesNotExist:
        since = None

    logger.info(f'Started Zotero update')

    items = items_to_dict(library_id, library_type, api_key, limit=limit, since_version=since)
    logger.info(f'Fetched {len(items.get('items', []))} items')

    created_count = 0
    for x in items.get('bibs', []):
        temp_item = create_zotitem(x)
        created_count += 1

    logger.info(f'Imported {created_count} models')

    return created_count