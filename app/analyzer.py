import re
import datetime
from datetime import date
from typing import Optional


class Analyzer:
    def __init__(self, text: list[dict] | None = None):
        self.text: list[dict] = text if text is not None else []

    def get_recite_metadata(self):
        self._cleansing()
        metadata = self.get_metadata()
        return metadata

    def _cleansing(self):
        for row in self.text:
            # 不要文字削除
            clean = re.sub(r"[^\w\u3040-\u30FF\u4E00-\u9FFF()-¥,.\\]+", "", row["text"])
            row["clean_text"] = clean

    def get_metadata(self):

        meta_data = {
            "registration_number": None,
            "tel_number": None,
            "date": None,
            "time": None,
        }

        for row in self.text:
            if meta_data['registration_number'] is None:
                meta_data['registration_number'] = self._get_registration_number(row["clean_text"])

            if meta_data['tel_number'] is None:
                meta_data['tel_number'] = self._get_tel_number(row["clean_text"])

            if meta_data['date'] is None:
                meta_data['date'] = self._get_date(row["clean_text"])

            if meta_data['time'] is None:
                meta_data['time'] = self._get_time(row["clean_text"])

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

        re_time = re.compile(r"(?P<h>(?:[01]?\d|2[0-3])):(?P<m>[0-5]\d)")

        text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        text = text.strip()

        # 年月日パターン
        m = re_time.search(text)
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

        regex = re.compile(
            r"(?<!\d)"  # 直前が数字ではない
            r"(?:0\d{1,4}-\d{1,4}-\d{4}"  # ハイフンあり
            r"|0\d{9,10})"  # ハイフンなし（0始まり10〜11桁）
            r"(?!\d)"  # 直後が数字ではない
        )
        if regex.search(text):
            tel_number = regex.search(text).group(0)

        return tel_number


    def _get_registration_number(self, text) -> str | None:
        registration_number = None

        regex = re.compile(r"(?<![0-9A-Za-z])T\d{13}(?![0-9A-Za-z])")

        if regex.search(text):
            registration_number = regex.search(text).group(0)

        return registration_number