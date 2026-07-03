import os
import img2pdf
from pdf2docx import Converter

input_files = "imgs/"


def create_pdf(input_files):
    temp_list = []

    # files need to be processed from a folder without writing their exact names
    for i in os.listdir(input_files):
        if i.endswith(".png") or i.endswith(".jpg"):
            temp_list.append(input_files + i)
        else:
            continue

    with open("output/output.pdf", "wb") as f:
        f.write(img2pdf.convert(temp_list))


def noOCR_pdf(input_pdf):
    cv = Converter(input_pdf)
    cv.convert("output/output.docx")
