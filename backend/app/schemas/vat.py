from pydantic import BaseModel
from typing import List, Optional

class VATJournalEntry(BaseModel):
    # Define fields based on koloni-vat.pdf
    # For example:
    # document_type: str
    # document_number: str
    # document_date: str
    # ...
    pass

class VATJournal(BaseModel):
    journal_type: str # "purchase" or "sales"
    entries: List[VATJournalEntry]

class VATBase(BaseModel):
    journals: List[VATJournal]

class VATCreate(VATBase):
    pass

class VATUpdate(VATBase):
    pass

class VAT(VATBase):
    id: int

    class Config:
        orm_mode = True
