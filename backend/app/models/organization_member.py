import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, UniqueConstraint

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class OrganizationRole(str, Enum):
    """Роли в организацията с йерархия: ADMIN > MANAGER > MEMBER"""

    ADMIN = "admin"  # Пълен достъп + управление на членове
    MANAGER = "manager"  # CRUD на всички бизнес обекти
    MEMBER = "member"  # Само четене + създаване


class OrganizationMemberBase(BaseModel):
    role: OrganizationRole = Field(default=OrganizationRole.MEMBER)
    is_active: bool = True


class OrganizationMemberCreate(BaseModel):
    user_id: uuid.UUID
    role: OrganizationRole = OrganizationRole.MEMBER


class OrganizationMemberUpdate(BaseModel):
    role: OrganizationRole | None = None
    is_active: bool | None = None


class OrganizationMember(OrganizationMemberBase, table=True):
    __tablename__ = "organization_member"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_org_member_user_org"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE"
    )
    date_joined: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="organization_memberships")
    organization: "Organization" = Relationship(back_populates="members")


class OrganizationMemberPublic(OrganizationMemberBase):
    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    date_joined: datetime
    date_updated: datetime


class OrganizationMembersPublic(BaseModel):
    data: list[OrganizationMemberPublic]
    count: int


# Helper function to check role hierarchy
def has_role_or_higher(member_role: OrganizationRole, required_role: OrganizationRole) -> bool:
    """Проверява дали член има дадената роля или по-висока."""
    role_hierarchy = {
        OrganizationRole.ADMIN: 3,
        OrganizationRole.MANAGER: 2,
        OrganizationRole.MEMBER: 1,
    }
    return role_hierarchy.get(member_role, 0) >= role_hierarchy.get(required_role, 0)
