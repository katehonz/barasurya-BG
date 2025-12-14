from sqlmodel import Session

from app import crud
from app.models import ItemUnit, ItemUnitCreate, Organization, User
from app.tests.conftest import create_organization_membership, create_test_organization
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_item_unit(
    db: Session,
    user: User | None = None,
    organization: Organization | None = None
) -> ItemUnit:
    if user is None:
        user = create_random_user(db)

    if organization is None:
        organization = create_test_organization(db)
        create_organization_membership(db, user, organization)

    organization_id = organization.id
    created_by_id = user.id
    assert organization_id is not None
    assert created_by_id is not None

    name = random_lower_string()
    description = random_lower_string()
    item_unit_in = ItemUnitCreate(name=name, description=description)
    return crud.create_item_unit(
        session=db,
        item_unit_in=item_unit_in,
        organization_id=organization_id,
        created_by_id=created_by_id
    )
