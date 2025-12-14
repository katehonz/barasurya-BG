import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.models import Store, OrganizationRole
from app.tests.conftest import (
    create_organization_membership,
    create_test_organization,
)
from app.tests.utils.store import create_random_store
from app.tests.utils.user import create_random_user, user_authentication_headers


def test_create_store(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)
    organization = create_test_organization(db)
    create_organization_membership(db, user, organization, OrganizationRole.ADMIN)
    user_token_headers = user_authentication_headers(
        client=client, email=user.email, password="testpassword123"
    )
    # Need to re-authenticate after membership creation
    from app.tests.utils.user import authentication_token_from_email
    user_token_headers = authentication_token_from_email(client=client, email=user.email, db=db)

    data = {"name": "Foo", "address": "St. Groove", "latitude": 7.534, "longitude": 112.8347}
    response = client.post(
        f"{settings.API_V1_STR}/stores/",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["address"] == data["address"]
    assert content["latitude"] == data["latitude"]
    assert content["longitude"] == data["longitude"]
    assert "id" in content
    assert "organization_id" in content


def test_read_store(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)
    organization = create_test_organization(db)
    create_organization_membership(db, user, organization, OrganizationRole.ADMIN)
    from app.tests.utils.user import authentication_token_from_email
    user_token_headers = authentication_token_from_email(client=client, email=user.email, db=db)
    store = create_random_store(db, user, organization)
    response = client.get(
        f"{settings.API_V1_STR}/stores/{store.id}",
        headers=user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == store.name
    assert content["address"] == store.address
    assert content["id"] == str(store.id)
    assert content["organization_id"] == str(store.organization_id)


def test_read_store_not_found(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)
    organization = create_test_organization(db)
    create_organization_membership(db, user, organization, OrganizationRole.ADMIN)
    from app.tests.utils.user import authentication_token_from_email
    user_token_headers = authentication_token_from_email(client=client, email=user.email, db=db)
    response = client.get(
        f"{settings.API_V1_STR}/stores/{uuid.uuid4()}",
        headers=user_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Store not found"


def test_read_store_not_enough_permissions(client: TestClient, db: Session) -> None:
    # Create a store in one organization
    user1 = create_random_user(db=db)
    org1 = create_test_organization(db)
    create_organization_membership(db, user1, org1, OrganizationRole.ADMIN)
    store = create_random_store(db, user1, org1)

    # Try to access from another organization
    user2 = create_random_user(db=db)
    org2 = create_test_organization(db)
    create_organization_membership(db, user2, org2, OrganizationRole.ADMIN)
    from app.tests.utils.user import authentication_token_from_email
    user2_token_headers = authentication_token_from_email(client=client, email=user2.email, db=db)

    response = client.get(
        f"{settings.API_V1_STR}/stores/{store.id}",
        headers=user2_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_stores(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)
    organization = create_test_organization(db)
    create_organization_membership(db, user, organization, OrganizationRole.ADMIN)
    from app.tests.utils.user import authentication_token_from_email
    user_token_headers = authentication_token_from_email(client=client, email=user.email, db=db)
    create_random_store(db, user, organization)
    create_random_store(db, user, organization)
    response = client.get(
        f"{settings.API_V1_STR}/stores/",
        headers=user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_store(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)
    organization = create_test_organization(db)
    create_organization_membership(db, user, organization, OrganizationRole.MANAGER)
    from app.tests.utils.user import authentication_token_from_email
    user_token_headers = authentication_token_from_email(client=client, email=user.email, db=db)
    store = create_random_store(db, user, organization)
    data = {"name": "Updated name", "address": "Updated address", "latitude": 8.324, "longitude": 113.324}
    response = client.put(
        f"{settings.API_V1_STR}/stores/{store.id}",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["address"] == data["address"]
    assert content["latitude"] == data["latitude"]
    assert content["longitude"] == data["longitude"]
    assert content["id"] == str(store.id)
    assert content["organization_id"] == str(store.organization_id)


def test_update_store_not_found(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)
    organization = create_test_organization(db)
    create_organization_membership(db, user, organization, OrganizationRole.MANAGER)
    from app.tests.utils.user import authentication_token_from_email
    user_token_headers = authentication_token_from_email(client=client, email=user.email, db=db)
    data = {"name": "Updated name", "address": "Updated address", "latitude": 8.324, "longitude": 113.324}
    response = client.put(
        f"{settings.API_V1_STR}/stores/{uuid.uuid4()}",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Store not found"


def test_update_store_requires_manager_role(client: TestClient, db: Session) -> None:
    # Member role cannot update
    user = create_random_user(db=db)
    organization = create_test_organization(db)
    create_organization_membership(db, user, organization, OrganizationRole.MEMBER)
    from app.tests.utils.user import authentication_token_from_email
    user_token_headers = authentication_token_from_email(client=client, email=user.email, db=db)

    # Create store as admin first
    admin = create_random_user(db=db)
    create_organization_membership(db, admin, organization, OrganizationRole.ADMIN)
    store = create_random_store(db, admin, organization)

    data = {"name": "Updated name", "address": "Updated address", "latitude": 8.324, "longitude": 113.324}
    response = client.put(
        f"{settings.API_V1_STR}/stores/{store.id}",
        headers=user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Requires manager role"


def test_delete_store(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)
    organization = create_test_organization(db)
    create_organization_membership(db, user, organization, OrganizationRole.MANAGER)
    from app.tests.utils.user import authentication_token_from_email
    user_token_headers = authentication_token_from_email(client=client, email=user.email, db=db)
    store = create_random_store(db, user, organization)
    response = client.delete(
        f"{settings.API_V1_STR}/stores/{store.id}",
        headers=user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Store deleted successfully"


def test_delete_store_not_found(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)
    organization = create_test_organization(db)
    create_organization_membership(db, user, organization, OrganizationRole.MANAGER)
    from app.tests.utils.user import authentication_token_from_email
    user_token_headers = authentication_token_from_email(client=client, email=user.email, db=db)
    response = client.delete(
        f"{settings.API_V1_STR}/stores/{uuid.uuid4()}",
        headers=user_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Store not found"


def test_delete_store_requires_manager_role(client: TestClient, db: Session) -> None:
    # Member role cannot delete
    user = create_random_user(db=db)
    organization = create_test_organization(db)
    create_organization_membership(db, user, organization, OrganizationRole.MEMBER)
    from app.tests.utils.user import authentication_token_from_email
    user_token_headers = authentication_token_from_email(client=client, email=user.email, db=db)

    # Create store as admin first
    admin = create_random_user(db=db)
    create_organization_membership(db, admin, organization, OrganizationRole.ADMIN)
    store = create_random_store(db, admin, organization)

    response = client.delete(
        f"{settings.API_V1_STR}/stores/{store.id}",
        headers=user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Requires manager role"
