import os
import img2pdf

input_files = "imgs/"


def create_pdf(input_files):
    temp_list = []

    # files need to be processed from a folder without writing their exact names
    for i in os.listdir(input_files):
        temp_list.append(input_files + i)

    print(temp_list)
    with open("output/output.pdf", "wb") as f:
        f.write(img2pdf.convert(temp_list))


create_pdf(input_files)
