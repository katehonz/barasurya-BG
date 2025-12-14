import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import (
    CurrentMembership,
    CurrentOrganization,
    CurrentUser,
    OrganizationRole,
    RequireAdmin,
    SessionDep,
)
from app.models import (
    BaseModelUpdate,
    Message,
    Organization,
    OrganizationCreate,
    OrganizationMember,
    OrganizationMemberCreate,
    OrganizationMemberPublic,
    OrganizationMembersPublic,
    OrganizationMemberUpdate,
    OrganizationPublic,
    OrganizationsPublic,
    OrganizationUpdate,
    User,
    has_role_or_higher,
)
from app.utils import utcnow

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=OrganizationsPublic)
def read_organizations(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve organizations the current user is a member of.
    """
    # Get organizations where user is a member
    count_statement = (
        select(func.count())
        .select_from(Organization)
        .join(OrganizationMember)
        .where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Organization)
        .join(OrganizationMember)
        .where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
        .offset(skip)
        .limit(limit)
    )
    organizations = session.exec(statement).all()

    return OrganizationsPublic(data=organizations, count=count)


@router.get("/current", response_model=OrganizationPublic)
def read_current_organization(current_org: CurrentOrganization) -> Any:
    """
    Get the current active organization.
    """
    return current_org


@router.get("/{id}", response_model=OrganizationPublic)
def read_organization(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get organization by ID.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if user is a member
    membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    ).first()

    if not membership and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    return org


@router.post("/", response_model=OrganizationPublic)
def create_organization(
    *, session: SessionDep, current_user: CurrentUser, org_in: OrganizationCreate
) -> Any:
    """
    Create new organization. The creating user becomes an admin.
    """
    # Check if slug already exists
    existing = session.exec(
        select(Organization).where(Organization.slug == org_in.slug)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Organization with this slug already exists"
        )

    # Create organization
    org = Organization.model_validate(org_in)
    session.add(org)
    session.commit()
    session.refresh(org)

    # Add creator as admin
    membership = OrganizationMember(
        user_id=current_user.id,
        organization_id=org.id,
        role=OrganizationRole.ADMIN,
    )
    session.add(membership)

    # Set as current organization if user has none
    if not current_user.current_organization_id:
        current_user.current_organization_id = org.id
        session.add(current_user)

    session.commit()
    session.refresh(org)
    return org


@router.put("/{id}", response_model=OrganizationPublic)
def update_organization(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    org_in: OrganizationUpdate,
) -> Any:
    """
    Update an organization. Requires admin role.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check admin permission
    membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    ).first()

    if not membership or membership.role != OrganizationRole.ADMIN:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Only admins can update the organization"
            )

    # Check slug uniqueness if changing
    if org_in.slug and org_in.slug != org.slug:
        existing = session.exec(
            select(Organization).where(Organization.slug == org_in.slug)
        ).first()
        if existing:
            raise HTTPException(
                status_code=400, detail="Organization with this slug already exists"
            )

    update_dict = org_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    org.sqlmodel_update(update_dict)
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


@router.delete("/{id}")
def delete_organization(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an organization. Requires admin role.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check admin permission
    membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    ).first()

    if not membership or membership.role != OrganizationRole.ADMIN:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Only admins can delete the organization"
            )

    # Clear current_organization_id for all users in this org
    members = session.exec(
        select(OrganizationMember).where(OrganizationMember.organization_id == id)
    ).all()
    for member in members:
        user = session.get(User, member.user_id)
        if user and user.current_organization_id == id:
            user.current_organization_id = None
            session.add(user)

    session.delete(org)
    session.commit()
    return Message(message="Organization deleted successfully")


@router.post("/{id}/switch", response_model=OrganizationPublic)
def switch_organization(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Switch to a different organization.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if not org.is_active:
        raise HTTPException(status_code=400, detail="Organization is inactive")

    # Check if user is a member
    membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    current_user.current_organization_id = id
    current_user.date_updated = utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(org)
    return org


# Member management endpoints


@router.get("/{id}/members", response_model=OrganizationMembersPublic)
def read_organization_members(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get members of an organization.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if user is a member
    membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    ).first()

    if not membership and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    count_statement = (
        select(func.count())
        .select_from(OrganizationMember)
        .where(OrganizationMember.organization_id == id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == id)
        .offset(skip)
        .limit(limit)
    )
    members = session.exec(statement).all()

    return OrganizationMembersPublic(data=members, count=count)


@router.post("/{id}/members", response_model=OrganizationMemberPublic)
def add_organization_member(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    member_in: OrganizationMemberCreate,
) -> Any:
    """
    Add a member to an organization. Requires admin role.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check admin permission
    admin_membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    ).first()

    if not admin_membership or admin_membership.role != OrganizationRole.ADMIN:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Only admins can add members"
            )

    # Check if user exists
    user = session.get(User, member_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already a member
    existing = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == member_in.user_id,
            OrganizationMember.organization_id == id,
        )
    ).first()

    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=400, detail="User is already a member of this organization"
            )
        # Reactivate membership
        existing.is_active = True
        existing.role = member_in.role
        existing.date_updated = utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    # Create new membership
    membership = OrganizationMember(
        user_id=member_in.user_id,
        organization_id=id,
        role=member_in.role,
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


@router.put("/{id}/members/{user_id}", response_model=OrganizationMemberPublic)
def update_organization_member(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    user_id: uuid.UUID,
    member_in: OrganizationMemberUpdate,
) -> Any:
    """
    Update a member's role. Requires admin role.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check admin permission
    admin_membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.organization_id == id,
            OrganizationMember.is_active == True,  # noqa: E712
        )
    ).first()

    if not admin_membership or admin_membership.role != OrganizationRole.ADMIN:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Only admins can update members"
            )

    # Get the membership to update
    membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == id,
        )
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    # Prevent removing the last admin
    if member_in.role and member_in.role != OrganizationRole.ADMIN:
        if membership.role == OrganizationRole.ADMIN:
            admin_count = session.exec(
                select(func.count())
                .select_from(OrganizationMember)
                .where(
                    OrganizationMember.organization_id == id,
                    OrganizationMember.role == OrganizationRole.ADMIN,
                    OrganizationMember.is_active == True,  # noqa: E712
                )
            ).one()
            if admin_count <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot remove the last admin from organization",
                )

    update_dict = member_in.model_dump(exclude_unset=True)
    update_dict["date_updated"] = utcnow()
    membership.sqlmodel_update(update_dict)
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


@router.delete("/{id}/members/{user_id}")
def remove_organization_member(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    user_id: uuid.UUID,
) -> Message:
    """
    Remove a member from an organization. Requires admin role.
    Users can also remove themselves.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Allow users to remove themselves, or require admin permission
    is_self = user_id == current_user.id

    if not is_self:
        admin_membership = session.exec(
            select(OrganizationMember).where(
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.organization_id == id,
                OrganizationMember.is_active == True,  # noqa: E712
            )
        ).first()

        if not admin_membership or admin_membership.role != OrganizationRole.ADMIN:
            if not current_user.is_superuser:
                raise HTTPException(
                    status_code=403, detail="Only admins can remove members"
                )

    # Get the membership to remove
    membership = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == id,
        )
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    # Prevent removing the last admin
    if membership.role == OrganizationRole.ADMIN:
        admin_count = session.exec(
            select(func.count())
            .select_from(OrganizationMember)
            .where(
                OrganizationMember.organization_id == id,
                OrganizationMember.role == OrganizationRole.ADMIN,
                OrganizationMember.is_active == True,  # noqa: E712
            )
        ).one()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last admin from organization",
            )

    # Clear current_organization_id if needed
    user = session.get(User, user_id)
    if user and user.current_organization_id == id:
        user.current_organization_id = None
        session.add(user)

    # Soft delete the membership
    membership.is_active = False
    membership.date_updated = utcnow()
    session.add(membership)
    session.commit()

    return Message(message="Member removed successfully")
