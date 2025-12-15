from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class JournalEntryLineBase(BaseModel):
    account_id: int
    description: Optional[str] = None
    debit: Optional[float] = None
    credit: Optional[float] = None
    contrahent_id: Optional[int] = None

class JournalEntryLineCreate(JournalEntryLineBase):
    pass

class JournalEntryLineUpdate(JournalEntryLineBase):
    pass

class JournalEntryLine(JournalEntryLineBase):
    id: int
    journal_entry_id: int

    class Config:
        orm_mode = True

class JournalEntryBase(BaseModel):
    date: date
    description: Optional[str] = None
    currency_code: str
    exchange_rate: Optional[float] = None

class JournalEntryCreate(JournalEntryBase):
    lines: List[JournalEntryLineCreate]

class JournalEntryUpdate(JournalEntryBase):
    lines: List[JournalEntryLineUpdate]

class JournalEntry(JournalEntryBase):
    id: int
    lines: List[JournalEntryLine] = []

    class Config:
        orm_mode = True
