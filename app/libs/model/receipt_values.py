import datetime
from pydantic import BaseModel
from typing import Optional

class ReceiptValues(BaseModel):
    store_name: Optional[str] = None
    registration_number: Optional[str] = None
    tel_number: Optional[str] = None
    date: Optional[datetime.date] = None
    time: Optional[datetime.time] = None
    sum: Optional[int] = None
