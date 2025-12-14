import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.organization_member import OrganizationMember
    from app.models.user_role import UserRole


# Shared properties
class UserBase(BaseModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Current active organization for the user
    current_organization_id: uuid.UUID | None = Field(
        default=None, foreign_key="organization.id", nullable=True, ondelete="SET NULL"
    )

    # Relationship to current organization
    current_organization: "Organization" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[User.current_organization_id]"}
    )

    # Organization memberships
    organization_memberships: list["OrganizationMember"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # User roles
    user_role: list["UserRole"] = Relationship(
        back_populates="user", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    current_organization_id: uuid.UUID | None
    date_created: datetime
    date_updated: datetime


class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int
