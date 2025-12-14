import uuid
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel


class SaftNc8TaricBase(BaseModel):
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True, nullable=False, ondelete="CASCADE")
    code: str
    description_bg: str
    year: int = Field(default=2026)
    primary_unit: Optional[str] = Field(default=None)
    secondary_unit: Optional[str] = Field(default=None)


class SaftNc8Taric(SaftNc8TaricBase, table=True):
    __tablename__ = 'saft_nc8_taric_codes'
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class SaftNc8TaricCreate(SaftNc8TaricBase):
    pass


class SaftNc8TaricRead(SaftNc8TaricBase):
    id: uuid.UUID

