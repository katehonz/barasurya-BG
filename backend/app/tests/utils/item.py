from sqlmodel import Session

from app import crud
from app.models import Item, ItemCreate, Organization, User
from app.tests.conftest import create_organization_membership, create_test_organization
from app.tests.utils.item_category import create_random_item_category
from app.tests.utils.item_unit import create_random_item_unit
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_item(
    db: Session,
    user: User | None = None,
    organization: Organization | None = None,
    **kwargs
) -> Item:
    if user is None:
        user = create_random_user(db)

    if organization is None:
        organization = create_test_organization(db)
        create_organization_membership(db, user, organization)

    organization_id = organization.id
    created_by_id = user.id
    assert organization_id is not None
    assert created_by_id is not None

    item_category = create_random_item_category(db, user, organization)
    item_category_id = item_category.id
    assert item_category_id is not None

    item_unit = create_random_item_unit(db, user, organization)
    item_unit_id = item_unit.id
    assert item_unit_id is not None

    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(
        title=title,
        description=description,
        item_category_id=item_category_id,
        item_unit_id=item_unit_id,
        **kwargs
    )
    return crud.create_item(
        session=db,
        item_in=item_in,
        organization_id=organization_id,
        created_by_id=created_by_id
    )
