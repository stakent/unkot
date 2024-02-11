from datetime import datetime

from celery import shared_task

from unkot.isap.fetch_isap_to_database import PublisherSymbol, fetch_isap_to_database
from unkot.isap.run_subscribed_searches import run_subscribed_searches


@shared_task
def fetch_isap_current_year():
    year = datetime.now().year
    fetch_isap_to_database(
        publisher=PublisherSymbol.ALL,
        year1=year,
        year2=year,
        new_only=True,
    )


@shared_task
def task_run_subscribed_searches():
    run_subscribed_searches()
