"fetch_isap_to_database "
import os.path
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from django.db import transaction
from structlog import get_logger

from unkot.isap.extract_text_from_deeds import extract_text_from_deed
from unkot.isap.models import NO_DATE_PROVIDED, Deed, DeedText, get_deed_file
from unkot.isap.serializers import ActInfo, ActsInYear

# Get an instance of a logger
log = get_logger()


def fetch_isap_deed_pdf(session: requests.Session, act_info: ActInfo) -> None:
    """Fetch deed from ISAP as pdf

    Parameters:

    session (requests.Session): session object used for requests to ISAP API
    act_info: ActInfo with act metedata

    Returns: nothing


    /isap/deeds/{publisher}/{year}/{position}/text.pdf
    returns deed text as pdf, up to somewhere between 2010 and 2000
    pdfs contain scans, after that pdf contain text.

    Do not fetch html text:
    /isap/deeds/{publisher}/{year}/{position}/text.html
    does sometimes return the deed text as html
    """
    # http://api.sejm.gov.pl/eli/acts/DU/2020/1/text.pdf

    url = f"http://api.sejm.gov.pl/eli/acts/{act_info.publisher}/{act_info.year}/{act_info.pos}/text.pdf"

    log.info("start fetch act as pdf", act_info=act_info)
    resp = session.get(url, stream=True)
    resp.raise_for_status()

    deed_pdf_file = get_deed_file(act_info=act_info, kind="pdf")
    pdf_data = resp.content
    if len(pdf_data) == 0:
        log.critical(
            f'fetch_isap_deed_pdf: got empty deed content for { act_info.address }'
        )
        sys.exit(1)
    os.makedirs(deed_pdf_file.parent, exist_ok=True)  # type: ignore
    with open(deed_pdf_file, "wb") as f:
        f.write(pdf_data)

    # log.info("end fetch act as pdf", act_info=act_info)


def replace_null_by_NO_DATE_PROVIDED(field):
    """replace None by NO_DATE_PROVIDED"""
    if field is None:
        value = NO_DATE_PROVIDED
    else:
        value = field
    return value


def fetch_isap_year_deeds(session, publisher, year: int, new_only: bool) -> int:
    """Fetch data from ISAP publisher's year index.
    If new_only==True then fetch:
        - new deeds
        - text of existing deeds without text
    """
    # bad http://isap.sejm.gov.pl/api/isap/acts/DU/2024
    # http://api.sejm.gov.pl/eli/acts/{publisher}/{year}
    url = "http://api.sejm.gov.pl/eli"
    url = url + f"/acts/{ publisher }/{ year }"
    log.info("fetching acts index", publisher=publisher, year=year)

    res = session.get(url)  # fetch index
    res.raise_for_status()

    acts_in_year = ActsInYear.model_validate(res.json())

    log.info("fetched acts list", number_of_acts=len(acts_in_year.items))

    n_deeds_fetched = 0
    for act_info in acts_in_year.items:
        with transaction.atomic():
            d, created = Deed.objects.get_or_create(address=act_info.address)
            if new_only and not created:
                dts = DeedText.objects.filter(deed_id=d.address)
                if dts.count() > 0 and dts[0].text != '':
                    continue
            d.publisher = act_info.publisher
            d.year = act_info.year
            d.volume = act_info.volume
            d.pos = act_info.pos
            d.deed_type = act_info.type
            d.title = act_info.title
            d.status = act_info.status
            d.display_address = act_info.display_address
            d.promulgation = replace_null_by_NO_DATE_PROVIDED(act_info.promulgation)
            d.announcement_date = replace_null_by_NO_DATE_PROVIDED(
                act_info.announcement_date
            )
            # 2023-10-12T10:46:30
            ts = datetime.strptime(act_info.change_date, "%Y-%m-%dT%H:%M:%S")
            ts2 = ts.replace(tzinfo=ZoneInfo("Europe/Warsaw"))
            d.change_date = ts2
            d.eli = act_info.eli
            d.save()
            try:
                fetch_isap_deed_pdf(session, act_info=act_info)
            except requests.exceptions.HTTPError as e:
                log.warning("error fetching pdf text", act_info=act_info, error=e)
                continue
            # pdf -> text -> db
            extract_text_from_deed(act_info=act_info, change_date=d.change_date)
            n_deeds_fetched = +1

    return n_deeds_fetched


def fetch_isap_to_database(publisher: str, year1, year2, new_only=False) -> int:
    """Fetch deed from ISAP, extract text and store in database.

    Parameters:
    publisher (str): symbol of the publisher:
        - 'ALL' for all konwn publishers
        - 'WDU' Dziennik Ustaw, od 1918, ~87000 deeds
        - 'WMP' Monitor Polski, od 1930, ~60000 deeds
        - 'LDU' Dziennik Ustaw, 1939-1990, ~1500 deeds
        - 'LMP' Monitor Polski, 1939-1940, 265 deeds
        - 'LDW' Dziennik Ustaw (Warszawski), 1944, 18 deeds
    year1 (int): oldest year of time range
    year2 (int): newest year of time range
    new_only (bool): fetch new deeds
    """
    session = requests.Session()

    if year1 > year2:
        raise ValueError('parameter "year1" has to be smaller or equal "year2"')

    n_deeds_fetched = 0
    if publisher == "ALL":
        publishers = ["WDU", "WMP"]
    else:
        publishers = [
            publisher,
        ]
    for year in range(year2, year1 - 1, -1):
        for publ in publishers:
            n_deeds_fetched += fetch_isap_year_deeds(session, publ, year, new_only)
    return n_deeds_fetched
