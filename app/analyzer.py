import json
import re
import datetime
from datetime import date
from pprint import pprint
from typing import Optional

from app.libs.model.receipt_values import ReceiptValues
from app.libs.model.sum_candidate import SumCandidate


class Analyzer:
    def __init__(self, lines: list[str]):
        self.lines: list[str] = lines
        self.cleaned_lines: list[str] = self._cleansing(lines)
        self.sum_candidates: dict[str, SumCandidate] = {}
        self.sum_flg = False


    @staticmethod
    def _cleansing(lines):
        cleaned_lines = []
        for line in lines:
            # 不要文字削除
            clean = re.sub(r"[^\w\u3040-\u30FF\u4E00-\u9FFF()-¥,. \\]+", "", line)
            cleaned_lines.append(clean)
        return cleaned_lines


    def get_receipt_value(self) -> ReceiptValues:
        receipt_values = ReceiptValues()

        for line in self.cleaned_lines:
            if receipt_values.registration_number is None:
                receipt_values.registration_number = self._get_registration_number(line)

            if receipt_values.tel_number is None:
                receipt_values.tel_number = self._get_tel_number(line)

            if receipt_values.date is None:
                receipt_values.date = self._get_date(line)

            if receipt_values.time is None:
                receipt_values.time = self._get_time(line)

            self._get_sum(line)

        # ストア名
        if receipt_values.store_name is None:
            receipt_values.store_name = self._get_store_name(receipt_values)

        # 合計金額
        if receipt_values.sum is None and self.sum_candidates:
            max_candidate = max(
                self.sum_candidates.values(),
                key=lambda candidate: candidate.score
            )
            sum_amount = max_candidate.value
            receipt_values.sum = sum_amount

        pprint(receipt_values)
        return receipt_values


    def _get_date(self, text) -> Optional[datetime.date]:
        rx_ymd_sep = re.compile(r"(?P<y>\d{4})[./-](?P<m>\d{1,2})[./-](?P<d>\d{1,2})")
        rx_ymd_jp = re.compile(r"(?P<y>\d{4})年(?P<m>\d{1,2})月(?P<d>\d{1,2})日?")
        rx_md_sep = re.compile(r"(?P<m>\d{1,2})[./-](?P<d>\d{1,2})")
        rx_md_jp = re.compile(r"(?P<m>\d{1,2})月(?P<d>\d{1,2})日?")

        text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        text = text.strip()

        # 年月日パターン
        for rx in (rx_ymd_sep, rx_ymd_jp):
            m = rx.search(text)
            if not m:
                continue
            try:
                y, mo, d = self._parse_ymd(m)
                return self._mk_date(y, mo, d)
            except ValueError:
                return None  # ここは continue にしてもOK（別表記を探すなら）

        return None


    def _get_time(self, text) -> Optional[datetime.time]:

        re_time1 = re.compile(r"(?P<h>(?:[01]?\d|2[0-3])):(?P<m>[0-5]\d)")
        re_time2 = re.compile(r"(?P<h>(?:[01]?\d|2[0-3]))時(?P<m>[0-5]\d)分")

        text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        text = text.strip()

        # 年月日パターン
        for rx in (re_time1, re_time2):
            m = rx.search(text)
            if m:
                try:
                    h, m = self._parse_hm(m)
                    return datetime.time(h, m)
                except ValueError:
                    return None  # ここは continue にしてもOK（別表記を探すなら）

        return None


    def _parse_ymd(self, m: re.Match[str]) -> tuple[int, int, int]:
        return int(m.group("y")), int(m.group("m")), int(m.group("d"))


    def _parse_hm(self, m: re.Match[str]) -> tuple[int, int]:
        return int(m.group("h")), int(m.group("m"))


    def _mk_date(self, y: int, m: int, d: int) -> date | None:
        try:
            target_date = datetime.date(y, m, d)
            today = datetime.date.today()

            if (today.year - target_date.year) >= 2:
                # システム日の年 - 対象日の年 が 2以上なら、システム日の年で日付を生成し
                target_date = self._get_latest_date(today.year, m, d)

            return target_date

        except ValueError:
            return None


    def _get_latest_date(self, y: int, m:int, d:int) -> date:
        target_date = datetime.date(y, m, d)
        if target_date > datetime.date.today():
            return datetime.date(datetime.date.today().year -1, m, d)
        return target_date


    def _get_tel_number(self, text) -> str | None:
        tel_number = None

        # -の前後のスペースを削除
        text = re.sub(r"\s*-\s*", "-", text)

        tel_rx = re.compile(
            r"(?<!\d)("
            r"0120-\d{3}-\d{3}"
            r"|"
            r"0\d{1,2}-\d{3,4}-\d{4}"
            r")(?!\d)"
        )

        m = tel_rx.search(text)
        if m:
            tel_number = m.group(1)

        return tel_number


    def _get_registration_number(self, text) -> str | None:
        registration_number = None

        regex = re.compile(r"(?<![0-9A-Za-z])[T1]\d{13}(?![0-9A-Za-z])")
        if regex.search(text):
            registration_number = regex.search(text).group(0)
            registration_number = f"T{registration_number[-13:]}"
            return registration_number

        regex = re.compile(r"(?=.*登録).*?(\d{13,14})")
        if regex.search(text):
            registration_number = regex.search(text).group(0)
            registration_number = f"T{registration_number[-13:]}"
            return registration_number

        return registration_number

    def _get_sum(self, text):
        # 合計 という文字列の後に登場する以下のような合計金額と思われる文字列を取得
        # 1,000
        # 12,345
        # 100
        # 1000
        # 上記の先頭に¥がつく場合も対象とする

        regex = re.compile(r"合計")
        if regex.search(text):
            self.sum_flg = True

        if self.sum_flg:
            m = re.search(r"(?:¥|￥|\\)?\s*(?P<amount>\d{1,3}(?:,\d{3})+|\d+)", text)
            if m:
                sum_amount = m.group("amount").replace(",", "")
                self.sum_candidates["total_after_sum"] = SumCandidate(
                    key="total_after_sum",
                    value=sum_amount,
                    score=1
                )
                return

        # 金額と思われる文字列の最大値を合計金額とみなす
        m = re.search(r"(?:¥|￥|\\)\s*(?P<amount>\d{1,3}(?:,\d{3})+|\d+)", text)
        if m:
            sum_amount = m.group("amount").replace(",", "")

            if not "start_¥mark_sum" in self.sum_candidates:
                self.sum_candidates["start_¥mark_sum"] = SumCandidate(
                    key="start_¥mark_sum",
                    value=sum_amount,
                    score=2
                )
                return

            if int(sum_amount) > self.sum_candidates["start_¥mark_sum"].value:
                self.sum_candidates["start_¥mark_sum"] = SumCandidate(
                    key="start_¥mark_sum",
                    value=sum_amount,
                    score=2
                )
            return


    def _get_store_name(self, receipt_values) -> str | None:

        stores = json.load(open("./store_data.json", "r", encoding="utf-8"))
        for store in stores:
            if store["registration_number"] == receipt_values.registration_number:
                return store["name"]
            if store["tel_number"] == receipt_values.tel_number:
                return store["name"]

        # 登録番号、電話番号で店舗名が見つからない場合、キーワードがレシート情報の文字列とマッチするかで、店舗名を取得する
        for store in stores:
            for keyword in store["keywords"]:
                for line in self.cleaned_lines:
                    if keyword in line:
                        return store["name"]

        return None
