import uuid

from sqlmodel import Session

from app.models import (
    Supplier,
    SupplierCreate,
)


def create_supplier(
    *, session: Session, supplier_in: SupplierCreate, organization_id: uuid.UUID, created_by_id: uuid.UUID
) -> Supplier:
    db_supplier = Supplier.model_validate(
        supplier_in,
        update={"organization_id": organization_id, "created_by_id": created_by_id}
    )
    session.add(db_supplier)
    session.commit()
    session.refresh(db_supplier)
    return db_supplier
