import uuid

from sqlmodel import Session

from app.models import (
    ItemUnit,
    ItemUnitCreate,
)


def create_item_unit(
    *, session: Session, item_unit_in: ItemUnitCreate, organization_id: uuid.UUID, created_by_id: uuid.UUID
) -> ItemUnit:
    db_item_unit = ItemUnit.model_validate(
        item_unit_in,
        update={"organization_id": organization_id, "created_by_id": created_by_id}
    )
    session.add(db_item_unit)
    session.commit()
    session.refresh(db_item_unit)
    return db_item_unit
