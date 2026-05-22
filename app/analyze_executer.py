import csv
from pathlib import Path
from analyzer import Analyzer
from libs.model.receipt_models import ReceiptResult
from result_output import ResultOutput

INPUT_PDF_DIR = "/receipts"
OUTPUT_DIR = "/output/"
YAYOI_CSV_FILE_PATH = "/output/yayoi.csv"

def execute():
    # 拡張子が.pdfのファイル一覧を取得する
    pdf_files = list(Path(INPUT_PDF_DIR).glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in the input directory.")
        return

    # pdfファイルパスをキーに解析結果を保持
    receipt_results:list[ReceiptResult] = []

    for pdf_file in pdf_files:
        # OCR文字列からレシートメタ情報を取得する
        analyzer = Analyzer(pdf_file)
        receipt_info = analyzer.get_receipt_info()
        receipt_results.append(ReceiptResult(pdf_file_path=pdf_file, receipt_info=receipt_info))

    # 解析結果を出力する
    result_output = ResultOutput(receipt_results, OUTPUT_DIR, YAYOI_CSV_FILE_PATH)
    result_output.output()


def rename_file():
    # YAYOI_CSV_FILE_PATH をループ処理し、B列の値のpdfをリネームする
    with open(YAYOI_CSV_FILE_PATH, "r", newline="", encoding="cp932") as file:
        reader = csv.reader(file)

        for row in reader:
            # 空行や列数不足の行はスキップ
            if len(row) < 26:
                continue

            current_pdf_name = row[1]  # B列: 現在のPDFファイル名
            transaction_date = row[3]  # D列: 取引日付
            amount = row[8]  # I列: 金額
            memo = row[16]  # Q列: 適用
            store_name = row[25]  # Z列: 店舗名

            if not current_pdf_name:
                continue

            safe_store_name = _sanitize_filename(store_name)
            new_pdf_name = f"{transaction_date}_{safe_store_name}_{memo}_{int(amount):,}.pdf"

            current_pdf_path = Path(OUTPUT_DIR) / f"{current_pdf_name}"
            new_pdf_path = Path(OUTPUT_DIR) / new_pdf_name

            if not current_pdf_path.exists():
                print(f"PDF file not found: {current_pdf_path}")
                continue

            current_pdf_path.rename(new_pdf_path)
            print(f"Renamed: {current_pdf_path} -> {new_pdf_path}")

def _sanitize_filename(value: str) -> str:
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        value = value.replace(char, "_")
    return value.strip()