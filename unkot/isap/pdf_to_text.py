"pdf_to_text "
import subprocess


def pdf_to_text(in_pdf_path, out_txt_path):
    """Convert pdf file to text file.

    Paramaters:
    in_pdf_path: full path to pdf to convert
    out_txt_dir: directory to save output text files

    """
    # make sure there is no gap between pages ranges

    PDFTOTEXT = "/usr/bin/pdftotext"

    subprocess.run(
        [PDFTOTEXT, in_pdf_path, out_txt_path],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
