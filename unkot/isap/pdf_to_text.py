"pdf_to_text "
import subprocess

import structlog
from structlog import get_logger

log = get_logger()


structlog.configure(
    processors=[
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
        # filter_f,  # <-- your processor!
        # structlog.processors.KeyValueRenderer(),
        structlog.dev.ConsoleRenderer(),
    ]
)


def pdf_to_text(in_pdf_path, out_txt_path):
    """Convert pdf file to text file.

    Paramaters:
    in_pdf_path: full path to pdf to convert
    out_txt_dir: directory to save output text files

    """
    # make sure there is no gap between pages ranges

    PDFTOTEXT = "/usr/bin/pdftotext"

    completed_process = subprocess.run(
        [PDFTOTEXT, in_pdf_path, out_txt_path],
        # check=True,
        capture_output=True,
    )
    if completed_process.returncode != 0:
        log.error(f"{PDFTOTEXT = } error:", stderr=completed_process.stderr)
        # raise ValueError(PDFTOTEXT)
    # completed_process.check_returncode()
