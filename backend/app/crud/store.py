import uuid

from sqlmodel import Session

from app.models import (
    Store,
    StoreCreate,
)


def create_store(
    *, session: Session, store_in: StoreCreate, organization_id: uuid.UUID, created_by_id: uuid.UUID
) -> Store:
    db_store = Store.model_validate(
        store_in,
        update={"organization_id": organization_id, "created_by_id": created_by_id}
    )
    session.add(db_store)
    session.commit()
    session.refresh(db_store)
    return db_store
