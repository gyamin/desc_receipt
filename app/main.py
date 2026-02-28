import pdfplumber

from app.analyzer import Analyzer

pdf_path = "../receipts/test3.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    lines = page.extract_text_lines()

if not lines:
    exit(1)

analyzer = Analyzer(lines)
metadata = analyzer.get_recite_metadata()

