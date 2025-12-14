from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import (
    CurrentUser,
    CurrentOrganization,
    SessionDep,
    get_current_active_superuser,
)
from app.models.asset import Asset, AssetCreate, AssetPublic, AssetsPublic, AssetUpdate
from app.services.asset import AssetService


router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/", response_model=AssetsPublic)
def list_assets(
    session: SessionDep,
    current_user: CurrentUser,
    current_organization: CurrentOrganization,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    category: str | None = None,
    search: str | None = None,
) -> Any:
    """
    List assets.
    """
    service = AssetService(session, current_user, current_organization)
    assets = service.list_assets(skip=skip, limit=limit, status=status, category=category, search=search)
    return AssetsPublic(data=assets, count=len(assets))


@router.post("/", response_model=AssetPublic)
def create_asset(
    asset_in: AssetCreate,
    session: SessionDep,
    current_user: CurrentUser,
    current_organization: CurrentOrganization,
) -> Any:
    """
    Create new asset.
    """
    service = AssetService(session, current_user, current_organization)
    asset = service.create_asset(asset_in)
    return asset


@router.get("/{asset_id}", response_model=AssetPublic)
def get_asset(
    asset_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    current_organization: CurrentOrganization,
) -> Any:
    """
    Get asset by ID.
    """
    service = AssetService(session, current_user, current_organization)
    asset = service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=AssetPublic)
def update_asset(
    asset_id: UUID,
    asset_in: AssetUpdate,
    session: SessionDep,
    current_user: CurrentUser,
    current_organization: CurrentOrganization,
) -> Any:
    """
    Update an asset.
    """
    service = AssetService(session, current_user, current_organization)
    asset = service.update_asset(asset_id, asset_in)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.delete("/{asset_id}", response_model=None)
def delete_asset(
    asset_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    current_organization: CurrentOrganization,
) -> Any:
    """
    Delete an asset. Only superuser can delete.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    service = AssetService(session, current_user, current_organization)
    asset = service.delete_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"message": "Asset deleted successfully"}


@router.get("/statistics", response_model=dict)
def get_asset_statistics(
    session: SessionDep,
    current_user: CurrentUser,
    current_organization: CurrentOrganization,
) -> Any:
    """
    Get asset statistics.
    """
    service = AssetService(session, current_user, current_organization)
    stats = service.get_assets_statistics()
    return stats
