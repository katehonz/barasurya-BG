
from typing import Optional

from sqlmodel import Field, SQLModel


class SaftNc8TaricBase(SQLModel):
    organization_id: int = Field(foreign_key="organization.id")
    code: str
    description_bg: str
    year: int = Field(default=2026)
    primary_unit: Optional[str] = Field(default=None)
    secondary_unit: Optional[str] = Field(default=None)


class SaftNc8Taric(SaftNc8TaricBase, table=True):
    __tablename__ = 'saft_nc8_taric_codes'
    id: Optional[int] = Field(default=None, primary_key=True)


class SaftNc8TaricCreate(SaftNc8TaricBase):
    pass


class SaftNc8TaricRead(SaftNc8TaricBase):
    id: int

