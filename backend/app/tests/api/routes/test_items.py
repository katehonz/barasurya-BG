import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Item, ItemCreate, StockLevel, Store


def test_read_item_with_stock(
    client: TestClient, session: Session, normal_user_token_headers: dict[str, str]
):
    # Create a store
    store = Store(name="Test Store", organization_id=uuid.uuid4(), created_by_id=uuid.uuid4())
    session.add(store)
    session.commit()
    session.refresh(store)

    # Create an item
    item_in = ItemCreate(title="Test Item", item_category_id=uuid.uuid4(), item_unit_id=uuid.uuid4())
    response = client.post(
        "/api/v1/items/",
        headers=normal_user_token_headers,
        json=item_in.dict(),
    )
    data = response.json()
    item_id = data["id"]

    # Create stock levels
    stock_level_1 = StockLevel(
        item_id=item_id,
        store_id=store.id,
        quantity=10,
        organization_id=uuid.uuid4(),
        created_by_id=uuid.uuid4(),
    )
    stock_level_2 = StockLevel(
        item_id=item_id,
        store_id=store.id,
        quantity=5,
        organization_id=uuid.uuid4(),
        created_by_id=uuid.uuid4(),
    )
    session.add(stock_level_1)
    session.add(stock_level_2)
    session.commit()

    # Read the item and check the stock
    response = client.get(f"/api/v1/items/{item_id}", headers=normal_user_token_headers)
    data = response.json()
    assert data["stock"] == 15