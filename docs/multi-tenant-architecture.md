# Мулти-тенант архитектура

## Обзор

Barasurya ERP използва мулти-тенант архитектура, която позволява:
- Потребители да членуват в множество организации
- Пълна изолация на данните между организациите
- Йерархия на роли с три нива на достъп

## Модели

### Organization

Основният модел за организация:

```python
class Organization(SQLModel, table=True):
    id: uuid.UUID
    name: str                    # Име на организацията
    slug: str                    # URL идентификатор (уникален)
    is_active: bool = True
    date_created: datetime
    date_updated: datetime
```

### OrganizationMember

Свързващ модел между потребители и организации:

```python
class OrganizationMember(SQLModel, table=True):
    id: uuid.UUID
    user_id: uuid.UUID           # FK -> user.id
    organization_id: uuid.UUID   # FK -> organization.id
    role: OrganizationRole       # admin, manager, member
    is_active: bool = True
    date_joined: datetime
```

### Роли и права

| Роля | Права |
|------|-------|
| **admin** | Пълен достъп + управление на членове + изтриване на организация |
| **manager** | CRUD на всички бизнес обекти |
| **member** | Четене + създаване (без изтриване) |

## Бизнес модели

Всички бизнес модели съдържат:

```python
organization_id: uuid.UUID  # FK -> organization.id (задължително)
created_by_id: uuid.UUID    # FK -> user.id (за audit trail)
```

### Списък на моделите с мулти-тенант поддръжка

- Account, AccountTransaction
- Customer, CustomerType
- Item, ItemCategory, ItemUnit
- Store, Supplier
- Purchase, PurchaseReturn
- Sale, SaleReturn
- Invoice, InvoiceLine
- Payment, Payable, Receivable
- StockAdjustment, StockTransfer
- Role, Permission

## API Dependencies

### CurrentOrganization

Извлича текущата организация от `user.current_organization_id`:

```python
@router.get("/")
def read_items(
    current_org: CurrentOrganization,
    ...
):
    statement = select(Item).where(Item.organization_id == current_org.id)
```

### CurrentMembership

Проверява членството и връща ролята:

```python
@router.delete("/{id}")
def delete_item(
    membership: CurrentMembership,
    ...
):
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(403, "Insufficient permissions")
```

### RequireAdmin / RequireManager

Декоратори за минимална роля:

```python
@router.post("/members")
def add_member(
    _: RequireAdmin,  # Само администратори
    ...
):
    pass
```

## API Endpoints

### Организации

| Метод | Път | Описание |
|-------|-----|----------|
| GET | `/organizations/` | Списък на организациите на потребителя |
| POST | `/organizations/` | Създаване (потребителят става admin) |
| GET | `/organizations/current` | Текуща активна организация |
| GET | `/organizations/{id}` | Детайли |
| PUT | `/organizations/{id}` | Редакция (само admin) |
| DELETE | `/organizations/{id}` | Изтриване (само admin) |
| POST | `/organizations/{id}/switch` | Превключване към организация |

### Членове

| Метод | Път | Описание |
|-------|-----|----------|
| GET | `/organizations/{id}/members` | Списък на членове |
| POST | `/organizations/{id}/members` | Добавяне на член (само admin) |
| PUT | `/organizations/{id}/members/{user_id}` | Промяна на роля |
| DELETE | `/organizations/{id}/members/{user_id}` | Премахване на член |

## Frontend

### useOrganization Hook

```typescript
const {
  organizations,           // Списък организации
  currentOrganization,     // Текуща организация
  switchTo,               // Превключване
  create,                 // Създаване
  hasOrganizations,       // Има ли организации
  needsOrganization,      // Трябва ли да създаде
} = useOrganization()
```

### OrganizationSwitcher Component

Компонент в страничната лента за:
- Показване на текущата организация
- Превключване между организации
- Създаване на нова организация

## Миграция

За активиране на мулти-тенант архитектурата:

```bash
cd backend
alembic upgrade head
```

## Примери

### Създаване на организация

```typescript
const { create } = useOrganization()

create({
  name: "Моята фирма",
  slug: "moiata-firma"
})
```

### Превключване между организации

```typescript
const { switchTo } = useOrganization()

switchTo(organizationId)
```

### API заявка с организация

```python
@router.post("/", response_model=ItemPublic)
def create_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    item_in: ItemCreate,
) -> Any:
    item = Item.model_validate(
        item_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(item)
    session.commit()
    return item
```
