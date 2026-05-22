import shutil
import datetime
import csv
from libs.model.receipt_models import ReceiptInfo, ReceiptResult


class ResultOutput:
    def __init__(self, receipt_results: list[ReceiptResult], pdf_output_dir: str, csv_file_path: str):
        self.receipt_results = receipt_results
        self.pdf_output_dir = pdf_output_dir
        self.csv_file_path = csv_file_path

    def output(self):
        self._pdf()
        self._yayoi_import_csv()


    def _pdf(self):
        index = 1
        for receipt_result in self.receipt_results:
            pdf_file_path = receipt_result.pdf_file_path

            # この段階のレシート解析からファイル名を決定しても不完全なので、ファイルを処理順に番号づけする
            output_filename = f"{index:04d}.pdf"
            shutil.copy(pdf_file_path, self.pdf_output_dir + output_filename)
            index += 1


    def _yayoi_import_csv(self):
        # csvファイルに出力する
        yayoi_import_csv = self.csv_file_path

        with open(yayoi_import_csv, "a", newline="", encoding="cp932") as file:
            writer = csv.writer(file)

            index = 1
            for receipt_result in self.receipt_results:

                receipt_info = receipt_result.receipt_info
                if not receipt_info.date: receipt_info.date = datetime.date.today()

                writer.writerow([
                    "2000",  # 識別フラグ
                    f"{index:04d}.pdf",   # 伝病No　pdfのファイル名として利用
                    None,   # 決算
                    receipt_info.date.strftime("%Y%m%d"),   # 取引日付
                    "雑費",   # 借方科目
                    None,   # 借方科目補助
                    None,   # 借方部門
                    None,   # 借方税区分
                    receipt_info.sum,   # 借方金額
                    None,   # 借方税金額
                    "普通預金",  # 貸方科目
                    None,
                    None,
                    None,
                    receipt_info.sum,  # 貸方金額
                    None,
                    None,     # 適用
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    receipt_info.store_name,
                    None,
                ])
                index += 1

