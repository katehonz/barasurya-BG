from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import User, Organization, OrganizationMember, OrganizationRole
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers
from app.utils import utcnow


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(OrganizationMember)
        session.exec(statement)
        statement = delete(Organization)
        session.exec(statement)
        statement = delete(User)
        session.exec(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c




@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


def create_test_organization(db: Session) -> Organization:
    """Create a test organization."""
    from app.tests.utils.utils import random_lower_string
    org = Organization(
        name=f"Test Org {random_lower_string()}",
        slug=random_lower_string(),
        is_active=True,
        date_created=utcnow(),
        date_updated=utcnow(),
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def create_organization_membership(
    db: Session,
    user: User,
    organization: Organization,
    role: OrganizationRole = OrganizationRole.ADMIN
) -> OrganizationMember:
    """Create an organization membership for a user."""
    membership = OrganizationMember(
        user_id=user.id,
        organization_id=organization.id,
        role=role,
        is_active=True,
        date_joined=utcnow(),
        date_updated=utcnow(),
    )
    db.add(membership)

    # Set current organization for user
    user.current_organization_id = organization.id
    db.add(user)

    db.commit()
    db.refresh(membership)
    return membership
