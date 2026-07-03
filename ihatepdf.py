import argparse
from pdf_functions import PDF

parser = argparse.ArgumentParser(description="IHatePDF cmd utility")

subparsers = parser.add_subparsers(dest="command", help="all commands")
subparsers.required = True

# create_pdf

parser_create = subparsers.add_parser("create", help="Make PDF from a picture/a folder with pictures")
parser_create.add_argument("input", "Path to a picture/a folder with pictures")
parser_create.add_argument("output", "Name and path where to output pdf. Ex.: result.pdf or output/result.pdf")

# convert_pdf

parser_create = subparsers.add_parser("convert", help="Convert PDF file to DOCX")
parser_create.add_argument("input", "Path to a picture/a folder with a pdf file")
parser_create.add_argument("output", "Name and path where to output docx. Ex.: result.docx or output/result.docx")

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

