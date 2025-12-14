from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.asset import Asset, AssetCreate, AssetUpdate
from app.models.user import User
from app.models.organization import Organization


class AssetService:
    def __init__(self, session: Session, current_user: User, current_organization: Organization):
        self.session = session
        self.current_user = current_user
        self.current_organization = current_organization

    def list_assets(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Asset]:
        query = select(Asset).where(Asset.organization_id == self.current_organization.id)
        if status:
            query = query.where(Asset.status == status)
        if category:
            query = query.where(Asset.category == category)
        if search:
            query = query.where(
                (Asset.name.ilike(f"%{search}%")) | 
                (Asset.code.ilike(f"%{search}%")) |
                (Asset.description.ilike(f"%{search}%"))
            )
        
        query = query.offset(skip).limit(limit)
        return self.session.exec(query).all()

    def create_asset(self, asset_in: AssetCreate) -> Asset:
        db_asset = Asset.from_orm(asset_in)
        db_asset.organization_id = self.current_organization.id
        db_asset.created_by_id = self.current_user.id
        self.session.add(db_asset)
        self.session.commit()
        self.session.refresh(db_asset)
        return db_asset

    def get_asset(self, asset_id: UUID) -> Optional[Asset]:
        query = select(Asset).where(
            Asset.id == asset_id, Asset.organization_id == self.current_organization.id
        )
        return self.session.exec(query).first()

    def update_asset(self, asset_id: UUID, asset_update: AssetUpdate) -> Optional[Asset]:
        db_asset = self.get_asset(asset_id)
        if not db_asset:
            return None
        
        asset_data = asset_update.model_dump(exclude_unset=True)
        for key, value in asset_data.items():
            setattr(db_asset, key, value)
        
        self.session.add(db_asset)
        self.session.commit()
        self.session.refresh(db_asset)
        return db_asset

    def delete_asset(self, asset_id: UUID) -> Optional[Asset]:
        db_asset = self.get_asset(asset_id)
        if not db_asset:
            return None
        
        self.session.delete(db_asset)
        self.session.commit()
        return db_asset
    
    # Placeholder for statistics, implement more complex logic later
    def get_assets_statistics(self) -> dict:
        total_assets = len(self.list_assets())
        active_assets = len(self.list_assets(status="active"))
        disposed_assets = len(self.list_assets(status="disposed"))
        
        return {
            "total_assets": total_assets,
            "active_assets": active_assets,
            "disposed_assets": disposed_assets,
        }
