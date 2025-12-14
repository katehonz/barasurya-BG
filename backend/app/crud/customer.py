import uuid

from sqlmodel import Session

from app.models import (
    Customer,
    CustomerCreate,
)


def create_customer(
    *, session: Session, customer_in: CustomerCreate, organization_id: uuid.UUID, created_by_id: uuid.UUID
) -> Customer:
    db_customer = Customer.model_validate(
        customer_in,
        update={"organization_id": organization_id, "created_by_id": created_by_id}
    )
    session.add(db_customer)
    session.commit()
    session.refresh(db_customer)
    return db_customer
