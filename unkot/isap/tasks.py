from datetime import datetime

from celery import shared_task

from unkot.isap.fetch_isap_to_database import fetch_isap_to_database


@shared_task
def fetch_isap_current_year():
    year = datetime.now().year
    fetch_isap_to_database(
        publisher='ALL',
        year1=year,
        year2=year,
        new_only=True,
    )
