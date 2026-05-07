from typing import Optional
from pydantic import BaseModel

class SumCandidate(BaseModel):
    key: Optional[str] = None
    score: float
    value: int