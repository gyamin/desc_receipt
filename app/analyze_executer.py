import shutil
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
from app.analyzer import Analyzer

INPUT_PDF_DIR = "./../receipts/"
OUTPUT_DIR = "./../output/"

def execute():
    # 拡張子が.pdfのファイル一覧を取得する
    pdf_files = list(Path(INPUT_PDF_DIR).glob("*.pdf"))


    for pdf_file in pdf_files:
        images = convert_from_path(
            pdf_file,
            dpi=300,
        )
        img = images[0]
        lines = pytesseract.image_to_string(
            img,
            lang="jpn+eng",  # 日本語+英数字
            config="--psm 6"  # ざっくり「ブロック内に複数行」想定。レシートに相性良いことが多い
        )
        # 改行で配列にsplit
        lines = lines.split("\n")

        # OCR文字列からレシートメタ情報を取得する
        analyzer = Analyzer(lines)
        metadata = analyzer.get_recite_metadata()

        # 解析結果からファイル名を生成して、pdfファイルをoutput_dirに保存
        output_filename = f"{metadata['date'].strftime("%Y%m%d")}_{metadata['store_name']}_{metadata['sum']}.pdf"

        shutil.copy(pdf_file, OUTPUT_DIR + output_filename)