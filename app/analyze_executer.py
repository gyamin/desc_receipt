import datetime
import shutil
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
from analyzer import Analyzer

INPUT_PDF_DIR = "/receipts"
OUTPUT_DIR = "/output/"

def execute():
    # 拡張子が.pdfのファイル一覧を取得する
    pdf_files = list(Path(INPUT_PDF_DIR).glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in the input directory.")
        return


    for pdf_file in pdf_files:
        images = convert_from_path(
            pdf_file,
            dpi=600,
        )
        img = images[0]
        lines = pytesseract.image_to_string(
            img,
            lang="jpn+eng",  # 日本語+英数字
            config="--psm 6"  # ざっくり「ブロック内に複数行」想定。レシートに相性良いことが多い
        )
        # 改行で配列にsplit
        lines = lines.split("\n")
        print(lines)

        # OCR文字列からレシートメタ情報を取得する
        analyzer = Analyzer(lines)
        receipt_values = analyzer.get_receipt_value()

        # 解析結果からファイル名を生成して、pdfファイルをoutput_dirに保存
        if not receipt_values.date:
            receipt_values.date = datetime.date.today()

        if not receipt_values.sum:
            receipt_values.sum = 0

        output_filename = f"{receipt_values.date.strftime("%Y%m%d")}_{receipt_values.store_name}_{receipt_values.sum:,}円.pdf"
        shutil.copy(pdf_file, OUTPUT_DIR + output_filename)