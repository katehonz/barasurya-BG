from sqlmodel import Session

from app import crud
from app.models import CustomerType, CustomerTypeCreate, Organization, User
from app.tests.conftest import create_organization_membership, create_test_organization
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_customer_type(
    db: Session,
    user: User | None = None,
    organization: Organization | None = None
) -> CustomerType:
    if user is None:
        user = create_random_user(db)

    if organization is None:
        organization = create_test_organization(db)
        create_organization_membership(db, user, organization)

    organization_id = organization.id
    created_by_id = user.id
    assert organization_id is not None
    assert created_by_id is not None

    data = {
        "name": random_lower_string(),
        "description": random_lower_string(),
    }
    customer_type_in = CustomerTypeCreate(**data)
    return crud.create_customer_type(
        session=db,
        customer_type_in=customer_type_in,
        organization_id=organization_id,
        created_by_id=created_by_id
    )
