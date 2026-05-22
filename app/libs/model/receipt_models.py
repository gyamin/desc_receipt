import datetime
from pathlib import Path
from pydantic import BaseModel
from typing import Optional

class ReceiptInfo(BaseModel):
    store_name: Optional[str] = None
    registration_number: Optional[str] = None
    tel_number: Optional[str] = None
    date: Optional[datetime.date] = None
    time: Optional[datetime.time] = None
    sum: Optional[int] = None

class ReceiptResult(BaseModel):
    pdf_file_path: Path
    receipt_info: ReceiptInfo