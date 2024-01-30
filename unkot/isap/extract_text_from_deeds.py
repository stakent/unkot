"extract_text_from_deeds "
import os.path
from datetime import datetime
from subprocess import CalledProcessError

from structlog import get_logger

from unkot.isap.models import Deed, DeedText, get_deed_file, save_deed_text
from unkot.isap.serializers import ActInfo

from .pdf_to_text import pdf_to_text

log = get_logger()


def extract_text_from_deed(act_info: ActInfo, change_date: datetime):
    in_pdf_path = get_deed_file(act_info=act_info, kind="pdf")
    # raise ValueError(f"{in_pdf_path = }")
    out_txt_path = get_deed_file(act_info=act_info, kind="txt")
    os.makedirs(out_txt_path.parent, exist_ok=True)  # type: ignore
    try:
        pdf_to_text(in_pdf_path, out_txt_path)
    except CalledProcessError as e:
        log.warning("pdf_to_text error", stderr=e.stderr)
        return
    try:
        with open(out_txt_path) as f:
            text = f.read()
    except FileNotFoundError as e:
        log.error(f"extract_text_from_deed error reading text from file { e }")
        return
    save_deed_text(act_info.address, change_date, text)


def extract_text_from_deeds():
    n = 0
    debug_step = 10
    t1 = datetime.now()
    log.info(f"extract_text_from_deeds started { t1 }")
    for deed in Deed.objects.all().order_by("-address"):
        count = DeedText.objects.filter(deed_id=deed.address).count()
        if count == 0:
            extract_text_from_deed(deed.address, deed.change_date, log)
        if n % debug_step == 0:
            t2 = datetime.now()
            dt = t2 - t1
            seconds = dt.total_seconds()
            deeds_per_second = debug_step / seconds
            print(f"====== { n } { deed.address } {deeds_per_second:.1f} deeds/s")
            t1 = t2
        n += 1
    log.info(f"extract_text_from_deeds finished { t1 }")
    return n
