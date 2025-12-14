from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_current_active_superuser, get_current_active_user, get_session, get_current_active_organization
from app.models.asset import Asset, AssetCreate, AssetPublic, AssetsPublic, AssetUpdate
from app.models.user import User
from app.models.organization import Organization
from app.services.asset import AssetService


router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/", response_model=AssetsPublic)
def list_assets(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    current_organization: Organization = Depends(get_current_active_organization),
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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    current_organization: Organization = Depends(get_current_active_organization),
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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    current_organization: Organization = Depends(get_current_active_organization),
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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    current_organization: Organization = Depends(get_current_active_organization),
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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_superuser), # Only superuser can delete
    current_organization: Organization = Depends(get_current_active_organization),
) -> Any:
    """
    Delete an asset.
    """
    service = AssetService(session, current_user, current_organization)
    asset = service.delete_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"message": "Asset deleted successfully"}

@router.get("/statistics", response_model=dict)
def get_asset_statistics(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    current_organization: Organization = Depends(get_current_active_organization),
) -> Any:
    """
    Get asset statistics.
    """
    service = AssetService(session, current_user, current_organization)
    stats = service.get_assets_statistics()
    return stats
