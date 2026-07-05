import os
import img2pdf
from pdf2docx import Converter
import pytesseract
from pdf2image import convert_from_path
from docx import Document


class PDF:
    def __init__(self, input_path, output):
        self.input_path = input_path
        self.output = output

        output_dir = os.path.dirname(self.output)

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

    def create_pdf(self):
        temp_list = []

        # files need to be processed from a folder without writing their exact names
        for i in sorted(os.listdir(self.input_path)):
            if i.lower().endswith((".png", ".jpg", ".jpeg")):
                temp_list.append(os.path.join(self.input_path, i))
            else:
                continue

        if not temp_list:
            print("Empty folder, no picture type files.")
            return

        with open(self.output, "wb") as f:
            f.write(img2pdf.convert(temp_list))

    def create_pdf_from_memory(self, images_bytes_list):
        if not images_bytes_list:
            return None

        pdf_bytes = img2pdf.convert(images_bytes_list)
        return pdf_bytes

    def convert_pdf(self):
        cv = Converter(self.input_path)
        cv.convert(self.output)
        cv.close()

    def OCR_convert_pdf(self):
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

        poppler_path = r"C:\poppler\poppler-26.02.0\Library\bin"

        images = convert_from_path(self.input_path, poppler_path=poppler_path)

        # print(pytesseract.get_languages(config=''))

        doc = Document()

        for image in images:
            # print(pytesseract.image_to_string(image, lang='rus+equ+osd'))

            output_text = pytesseract.image_to_string(image, lang="rus")

            doc.add_paragraph(output_text)

        doc.save(self.output)
