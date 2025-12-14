from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import (
    Organization,
    OrganizationMember,
    OrganizationRole,
    Permission,
    RolePermission,
    TokenPayload,
    User,
    UserRole,
    has_role_or_higher,
)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def has_permission(session: SessionDep, user: User, permission_name: str) -> bool:
    role_permissions = session.exec(
        select(Permission.name)
        .join(RolePermission)
        .join(UserRole, RolePermission.role_id == UserRole.role_id)
        .where(UserRole.user_id == user.id)
    ).all()
    if permission_name in role_permissions:
        return True
    return False


def permission_required(permission_name: str):
    def dependency(session: SessionDep, current_user: CurrentUser):
        if not has_permission(session, current_user, permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    return dependency


# Organization-related dependencies


def get_current_organization(
    session: SessionDep, current_user: CurrentUser
) -> Organization:
    """
    Get the user's current active organization.
    Raises 400 if user has no current organization set.
    """
    if not current_user.current_organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No organization selected. Please select an organization first.",
        )

    org = session.get(Organization, current_user.current_organization_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    if not org.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization is inactive",
        )

    return org


CurrentOrganization = Annotated[Organization, Depends(get_current_organization)]


def get_organization_membership(
    session: SessionDep, current_user: CurrentUser, current_org: CurrentOrganization
) -> OrganizationMember:
    """
    Get the user's membership in the current organization.
    Raises 403 if user is not a member.
    """
    membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == current_org.id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )

    return membership


CurrentMembership = Annotated[OrganizationMember, Depends(get_organization_membership)]


def require_org_role(min_role: OrganizationRole):
    """
    Dependency factory that requires a minimum organization role.
    Role hierarchy: ADMIN > MANAGER > MEMBER
    """

    def dependency(membership: CurrentMembership) -> OrganizationMember:
        if not has_role_or_higher(membership.role, min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires at least {min_role.value} role",
            )
        return membership

    return dependency


# Convenience dependencies for common role checks
RequireAdmin = Annotated[OrganizationMember, Depends(require_org_role(OrganizationRole.ADMIN))]
RequireManager = Annotated[OrganizationMember, Depends(require_org_role(OrganizationRole.MANAGER))]
RequireMember = Annotated[OrganizationMember, Depends(require_org_role(OrganizationRole.MEMBER))]
