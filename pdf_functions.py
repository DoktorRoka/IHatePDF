import os
import img2pdf
from pdf2docx import Converter


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

    def convert_pdf(self):
        cv = Converter(self.input_path)
        cv.convert(self.output)
        cv.close()
