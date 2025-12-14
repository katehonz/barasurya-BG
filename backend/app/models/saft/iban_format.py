
from typing import Optional

from sqlmodel import Field, SQLModel


class SaftIBANFormatBase(SQLModel):
    country: str
    country_code: str = Field(max_length=2, index=True, unique=True, sa_column_kwargs={"unique": True})
    char_count: int
    bank_code_format: Optional[str] = Field(default=None)
    iban_fields: Optional[str] = Field(default=None)
    comments: Optional[str] = Field(default=None)


class SaftIBANFormat(SaftIBANFormatBase, table=True):
    __tablename__ = 'saft_iban_formats'
    id: Optional[int] = Field(default=None, primary_key=True)


class SaftIBANFormatCreate(SaftIBANFormatBase):
    pass


class SaftIBANFormatRead(SaftIBANFormatBase):
    id: int

