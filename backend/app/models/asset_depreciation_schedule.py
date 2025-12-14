
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.organization import Organization
    from app.models.user import User


class AssetDepreciationScheduleBase(SQLModel):
    depreciation_date: date
    amount: float
    book_value: float


class AssetDepreciationScheduleCreate(AssetDepreciationScheduleBase):
    asset_id: uuid.UUID


class AssetDepreciationScheduleUpdate(AssetDepreciationScheduleBase):
    pass


class AssetDepreciationSchedule(AssetDepreciationScheduleBase, table=True):
    __tablename__ = "asset_depreciation_schedule"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    asset_id: uuid.UUID = Field(
        foreign_key="asset.id", nullable=False, ondelete="CASCADE"
    )

    organization: "Organization" = Relationship()
    created_by: "User" = Relationship()
    asset: "Asset" = Relationship(back_populates="depreciation_schedule")


class AssetDepreciationSchedulePublic(AssetDepreciationScheduleBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    asset_id: uuid.UUID
    date_created: datetime


class AssetDepreciationSchedulesPublic(SQLModel):
    data: list[AssetDepreciationSchedulePublic]
    count: int
