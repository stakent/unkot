"fetch_isap_to_database "
import logging
import os.path
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from django.db import transaction

from unkot.isap.extract_text_from_deeds import extract_text_from_deed
from unkot.isap.models import NO_DATE_PROVIDED, Deed, DeedText, get_deed_pdf_dir

# Get an instance of a logger
logger = logging.getLogger(__name__)


def fetch_isap_deed_pdf(session, publisher, year, position):
    """Fetch deed from ISAP as pdf

    Parameters:

    session (requests.Session): session object used for requests to ISAP API
    publisher (str): symbol of the publication
            "WDU" "Dz.U." "Dziennik Ustaw"
            "WMP" "M.P." "Monitor Polski"
            and more
    year (int): year of the publication of the deed
    position (int): sequential number of the deed in the year

    Returns: nothing


    /isap/deeds/{publisher}/{year}/{position}/text.pdf
    returns deed text as pdf, up to somewhere between 2010 and 2000
    pdfs contain scans, after that pdf contain text.

    Do not fetch html text:
    /isap/deeds/{publisher}/{year}/{position}/text.html
    does sometimes return the deed text as html
    """
    # address WDU20220000010
    #                1234567
    address = f"{ publisher }{ year }{position:07d}"
    url = "http://isap.sejm.gov.pl/api"
    url = url + f"/isap/deeds/{publisher}/{year}/{position}/text."
    resp = session.get(url + "pdf", stream=True)
    resp.raise_for_status()

    print(f"======= fetch_isap_deed_pdf: { address } pdf")

    deed_pdf_dir = get_deed_pdf_dir(address)
    fp = os.path.join(deed_pdf_dir, address + ".pdf")
    pdf_data = resp.raw.read()
    os.makedirs(deed_pdf_dir, exist_ok=True)
    with open(fp, "wb") as f:
        f.write(pdf_data)


def replace_null_by_NO_DATE_PROVIDED(field):
    """replace None by NO_DATE_PROVIDED"""
    if field is None:
        value = NO_DATE_PROVIDED
    else:
        value = field
    return value


def fetch_isap_year_deeds(session, publisher, year, new_only, log):
    """Fetch data from ISAP publisher's year index.
    If new_only==True then fetch:
        - new deeds
        - text of existing deeds without text
    """
    url = "http://isap.sejm.gov.pl/api"
    url = url + f"/isap/acts/{ publisher }/{ year }"
    logger.info(f"==== fetching { publisher } index for { year }")
    n_deeds_fetched = 0
    res = session.get(url)  # fetch index
    res.raise_for_status()
    js = res.json()
    items = js["items"]
    for item in items:
        with transaction.atomic():
            d, created = Deed.objects.get_or_create(address=item["address"])
            if new_only and not created:
                dts = DeedText.objects.filter(deed_id=d.address)
                if dts.count() > 0 and dts[0].text != '':
                    continue
            d.publisher = item["publisher"]
            d.year = int(item["year"])
            d.volume = int(item["volume"])
            d.pos = int(item["pos"])
            d.deed_type = item["type"]
            d.title = item["title"]
            d.status = item["status"]
            d.display_address = item["displayAddress"]
            d.promulgation = replace_null_by_NO_DATE_PROVIDED(item["promulgation"])
            d.announcement_date = replace_null_by_NO_DATE_PROVIDED(
                item["announcementDate"]
            )
            ts = datetime.strptime(item["changeDate"], "%Y-%m-%d %H:%M:%S")
            ts = ts.replace(tzinfo=ZoneInfo("Europe/Warsaw"))
            d.change_date = ts
            d.eli = item["ELI"]
            d.save()
            try:
                fetch_isap_deed_pdf(session, d.publisher, d.year, d.pos)
            except requests.exceptions.HTTPError as e:
                log.warning(f'error fetching pdf text for { d.address }: "{ e }"')
                continue
            # pdf -> text -> db
            extract_text_from_deed(
                address=d.address, change_date=d.change_date, log=log
            )
            n_deeds_fetched = +1
    return n_deeds_fetched


def fetch_isap_to_database(publisher, year1, year2, new_only=False, log=None):
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
            n_deeds_fetched += fetch_isap_year_deeds(
                session, publ, year, new_only, log=logger
            )
    return n_deeds_fetched
