import img2pdf


class PDF:
    def __init__(self):
        pass

    def create_pdf_from_memory(self, images_bytes_list):
        if not images_bytes_list:
            return None

        pdf_bytes = img2pdf.convert(images_bytes_list)
        return pdf_bytes
