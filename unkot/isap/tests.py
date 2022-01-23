import os
import tempfile

from django.test import SimpleTestCase

from .pdf_to_text import pdf_to_text


class DeedTextTestCase(SimpleTestCase):
    def setUp(self):
        pass

    def test_pdf_to_text(self):
        address = "WMP20220000006"
        test_pdf_fn = f"unkot/isap/test_data/{ address }.pdf"
        out_txt_name = f"{ address }.txt"

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_txt_path = os.path.join(tmp_dir, out_txt_name)
            pdf_to_text(test_pdf_fn, out_txt_path)
            with open(out_txt_path, "r") as f:
                text = f.read()
        # print(f'==== text: { text }', flush=True)

        self.assertTrue("Warszawa, dnia 4 stycznia 2022 r." in text)
        self.assertTrue("„Zespołem”." in text)
        self.assertTrue("rozwiązań technicznych oraz organizacyjnych dla" in text)
