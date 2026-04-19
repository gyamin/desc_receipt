import json
import os
import re
import datetime
from datetime import date
from typing import Optional


class Analyzer:
    def __init__(self, lines: list[str] | None = None):
        self.lines: list[str] = lines if lines is not None else []
        self.cleaned_lines: list[str] = []
        self.sum_flg = False

    def get_recite_metadata(self):
        self._cleansing()
        metadata = self.get_metadata()
        return metadata

    def _cleansing(self):
        for line in self.lines:
            # 不要文字削除
            clean = re.sub(r"[^\w\u3040-\u30FF\u4E00-\u9FFF()-¥,.\\]+", "", line)
            self.cleaned_lines.append(clean)
            print(clean)

    def get_metadata(self):

        meta_data = {
            "store_name": None,
            "registration_number": None,
            "tel_number": None,
            "date": None,
            "time": None,
            "sum": None
        }

        for line in self.cleaned_lines:
            if meta_data['registration_number'] is None:
                meta_data['registration_number'] = self._get_registration_number(line)

            if meta_data['tel_number'] is None:
                meta_data['tel_number'] = self._get_tel_number(line)

            if meta_data['date'] is None:
                meta_data['date'] = self._get_date(line)

            if meta_data['time'] is None:
                meta_data['time'] = self._get_time(line)

            if meta_data['sum'] is None:
                meta_data['sum'] = self._get_sum_amount(line)

            if meta_data['store_name'] is None:
                meta_data['store_name'] = self._get_store_name(meta_data)

        print(meta_data)
        return meta_data

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

        rx = re.compile(
            r"(?<!\d)("
            r"0120-\d{3}-\d{3}"  # 0120-295-770
            r"|0\d{1,4}-\d{1,4}-\d{3,4}"  # 03-1234-5678 / 099-123-4567 等（ざっくり許容）
            r"|0\d{9,10}"  # 0始まり10〜11桁（ハイフンなし）
            r")(?!\d)"
        )
        if rx.search(text):
            tel_number = rx.search(text).group(0)

        return tel_number


    def _get_registration_number(self, text) -> str | None:
        registration_number = None

        regex = re.compile(r"(?<![0-9A-Za-z])T\d{13}(?![0-9A-Za-z])")

        if regex.search(text):
            registration_number = regex.search(text).group(0)

        return registration_number


    def _get_sum_amount(self, text) -> str | None:
        sum_amount = None

        regex = re.compile(r"合計")

        if regex.search(text):
            self.sum_flg = True

        if not self.sum_flg:
            return None

        num_full_re = re.compile(r"\d{1,3}(?:,\d{3})*$")
        if num_full_re.search(text):
            sum_amount = num_full_re.search(text).group(0)
            sum_amount = sum_amount.replace(",", "")

        return sum_amount


    def _get_store_name(self, metadata) -> str | None:

        stores = json.load(open("./store_data.json", "r", encoding="utf-8"))
        for store in stores:
            if store["registration_number"] == metadata["registration_number"]:
                return store["name"]
            if store["tel_number"] == metadata["tel_number"]:
                return store["name"]
        return None
