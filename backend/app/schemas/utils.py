from pydantic import BaseModel

class InvoiceType(BaseModel):
    code: str
    name: str
