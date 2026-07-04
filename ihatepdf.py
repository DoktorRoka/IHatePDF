import argparse
from pdf_functions import PDF

parser = argparse.ArgumentParser(description="IHatePDF cmd utility")

subparsers = parser.add_subparsers(dest="command", help="all commands")
subparsers.required = True

# create_pdf

parser_create = subparsers.add_parser(
    "create", help="Make PDF from a picture/a folder with pictures"
)
parser_create.add_argument("input", help="Path to a picture/a folder with pictures")
parser_create.add_argument(
    "output",
    help="Name and path where to output pdf. Ex.: result.pdf or output/result.pdf",
)

# convert_pdf

parser_convert = subparsers.add_parser("convert", help="Convert PDF file to DOCX")
parser_convert.add_argument("input", help="Path to a pdf file")
parser_convert.add_argument(
    "output",
    help="Name and path where to output docx. Ex.: result.docx or output/result.docx",
)

# ocr_pdf

parser_convert = subparsers.add_parser("ocr", help="Convert PDF file to DOCX with OCR")
parser_convert.add_argument("input", help="Path to a pdf file")
parser_convert.add_argument(
    "output",
    help="Name and path where to output docx. Ex.: result.docx or output/result.docx",
)


if __name__ == "__main__":
    args = parser.parse_args()

    ihatepdf = PDF(args.input, args.output)

    if args.command == "create":
        print("Compiling pdf file...")
        ihatepdf.create_pdf()
        print("Done.")

    elif args.command == "convert":
        print("Converting into docx...")
        ihatepdf.convert_pdf()
        print("Done.")

    elif args.command == "ocr":
        print("Converting into docx with ocr...")
        ihatepdf.OCR_convert_pdf()
        print("Done.")
