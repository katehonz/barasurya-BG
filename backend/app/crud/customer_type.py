import uuid

from sqlmodel import Session

from app.models import (
    CustomerType,
    CustomerTypeCreate,
)


def create_customer_type(
    *, session: Session, customer_type_in: CustomerTypeCreate, organization_id: uuid.UUID, created_by_id: uuid.UUID
) -> CustomerType:
    db_customer_type = CustomerType.model_validate(
        customer_type_in,
        update={"organization_id": organization_id, "created_by_id": created_by_id}
    )
    session.add(db_customer_type)
    session.commit()
    session.refresh(db_customer_type)
    return db_customer_type
