from sqlmodel import Session

from app import crud
from app.models import Organization, Store, StoreCreate, User
from app.tests.conftest import create_organization_membership, create_test_organization
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_latitude, random_longitude, random_lower_string


def create_random_store(
    db: Session,
    user: User | None = None,
    organization: Organization | None = None
) -> Store:
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
        "address": random_lower_string(),
        "latitude": random_latitude(),
        "longitude": random_longitude(),
    }
    store_in = StoreCreate(**data)
    return crud.create_store(
        session=db,
        store_in=store_in,
        organization_id=organization_id,
        created_by_id=created_by_id
    )
