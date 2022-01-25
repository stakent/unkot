"extract_text_from_deeds "
import datetime
import os.path
from subprocess import CalledProcessError

from isap.pdf_to_text import pdf_to_text

from unkot.isap.models import (
    Deed,
    DeedText,
    get_deed_pdf_dir,
    get_deed_text_dir,
    save_deed_text,
)


def extract_text_from_deed(address, change_date, log):
    in_pdf_path = os.path.join(get_deed_pdf_dir(address), address + ".pdf")
    out_txt_path = os.path.join(get_deed_text_dir(address), address + ".txt")
    try:
        os.mkdir(get_deed_text_dir(address))
    except FileExistsError:
        pass
    try:
        pdf_to_text(in_pdf_path, out_txt_path)
    except CalledProcessError as e:
        log.fatal(f"{ __file__ } { e }")
        # log.error(f"{ __file__ } { e }")
        # return
    try:
        with open(out_txt_path, "r") as f:
            text = f.read()
    except FileNotFoundError as e:
        log.error(f"extract_text_from_deed error reading text from file { e }")
        return
    save_deed_text(address, change_date, text)


def extract_text_from_deeds(log):
    n = 0
    debug_step = 10
    t1 = datetime.datetime.now()
    log.error(f"extract_text_from_deeds started { t1 }")
    for deed in Deed.objects.all().order_by("-address").values("address"):
        # fp = os.path.join(data_dir, deed.address + '.pdf')
        address = deed["address"]
        count = DeedText.objects.filter(deed_id=address).count()
        if count == 0:
            extract_text_from_deed(address, deed.change_date, log)
        if n % debug_step == 0:
            t2 = datetime.datetime.now()
            dt = t2 - t1
            seconds = dt.total_seconds()
            deeds_per_second = debug_step / seconds
            print(f"====== { n } { address } {deeds_per_second:.1f} deeds/s")
            t1 = t2
        n += 1
    log.info(f"extract_text_from_deeds finished { t1 }")
    return n
