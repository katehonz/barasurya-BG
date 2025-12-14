import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import (
    CurrentMembership,
    CurrentOrganization,
    CurrentUser,
    RequireAdmin,
    SessionDep,
)
from app.models import (
    BaseModelUpdate,
    Message,
    OrganizationRole,
    Permission,
    PermissionCreate,
    PermissionPublic,
    PermissionsPublic,
    PermissionUpdate,
    has_role_or_higher,
)

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("/", response_model=PermissionsPublic)
def read_permissions(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve permissions for the current organization. Requires admin role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.ADMIN):
        raise HTTPException(status_code=403, detail="Requires admin role")

    count_statement = (
        select(func.count())
        .select_from(Permission)
        .where(Permission.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Permission)
        .where(Permission.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    permissions = session.exec(statement).all()

    return PermissionsPublic(data=permissions, count=count)


@router.get("/{id}", response_model=PermissionPublic)
def read_permission(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get permission by ID. Requires admin role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.ADMIN):
        raise HTTPException(status_code=403, detail="Requires admin role")

    permission = session.get(Permission, id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    if permission.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return permission


@router.post("/", response_model=PermissionPublic)
def create_permission(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    permission_in: PermissionCreate,
) -> Any:
    """
    Create new permission. Requires admin role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.ADMIN):
        raise HTTPException(status_code=403, detail="Requires admin role")

    permission = Permission.model_validate(
        permission_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
            "editor_id": current_user.id,
        },
    )
    session.add(permission)
    session.commit()
    session.refresh(permission)
    return permission


@router.put("/{id}", response_model=PermissionPublic)
def update_permission(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    permission_in: PermissionUpdate,
) -> Any:
    """
    Update a permission. Requires admin role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.ADMIN):
        raise HTTPException(status_code=403, detail="Requires admin role")

    permission = session.get(Permission, id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    if permission.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = permission_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    update_dict["editor_id"] = current_user.id
    permission.sqlmodel_update(update_dict)
    session.add(permission)
    session.commit()
    session.refresh(permission)
    return permission


@router.delete("/{id}")
def delete_permission(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete a permission. Requires admin role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.ADMIN):
        raise HTTPException(status_code=403, detail="Requires admin role")

    permission = session.get(Permission, id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    if permission.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(permission)
    session.commit()
    return Message(message="Permission deleted successfully")
