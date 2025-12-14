# Многонаемна архитектура

## Обзор

Barasurya ERP използва многонаемна архитектура (multi-tenant), която позволява:
- Потребителите да членуват в множество организации.
- Пълна изолация на данните между отделните организации.
- Йерархия на ролите с три нива на достъп.

## Модели на данните

### Organization

Основният модел, представящ една организация:

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

Свързващ модел между потребители (`User`) и организации (`Organization`), който дефинира ролята на потребителя в рамките на организацията:

```python
class OrganizationMember(SQLModel, table=True):
    id: uuid.UUID
    user_id: uuid.UUID           # Външен ключ към `user.id`
    organization_id: uuid.UUID   # Външен ключ към `organization.id`
    role: OrganizationRole       # Роля: admin, manager, member
    is_active: bool = True
    date_joined: datetime
```

### Роли и права

| Роля | Права |
|------|-------|
| **admin** | Пълен достъп до всички ресурси, управление на членове и изтриване на организацията. |
| **manager** | Създаване, четене, редакция и изтриване (CRUD) на всички бизнес обекти. |
| **member** | Четене на данни и създаване на нови записи (без право на редакция или изтриване). |

## Бизнес модели

Всички бизнес модели, които са обвързани с конкретна организация, съдържат следните две полета:

```python
organization_id: uuid.UUID  # Задължителен външен ключ към `organization.id`
created_by_id: uuid.UUID    # Външен ключ към `user.id` (за проследяване на промените)
```

### Списък на моделите с многонаемна поддръжка

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

## API зависимости (Dependencies)

### CurrentOrganization

FastAPI зависимост, която извлича текущата активна организация за потребителя. ID-то на организацията се взима от полето `user.current_organization_id`. По този начин всички заявки автоматично се филтрират за конкретната организация.

```python
@router.get("/")
def read_items(
    current_org: CurrentOrganization, # Инжектиране на текущата организация
    ...
):
    # Заявките към базата данни се филтрират по `organization_id`
    statement = select(Item).where(Item.organization_id == current_org.id)
```

### CurrentMembership

Тази зависимост проверява дали текущият потребител е член на организацията, до чиито ресурси се опитва да достъпи. Връща информация за членството, включително ролята на потребителя, която се използва за проверка на правата.

```python
@router.delete("/{id}")
def delete_item(
    membership: CurrentMembership, # Инжектиране на членството
    ...
):
    # Проверка дали ролята е достатъчно висока
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(403, "Insufficient permissions")
```

### RequireAdmin / RequireManager

Декоратори, които опростяват проверката за минимална роля. Ако потребителят няма необходимата роля, заявката се прекратява с грешка 403 (Forbidden).

```python
@router.post("/members")
def add_member(
    _: RequireAdmin,  # Достъп само за администратори
    ...
):
    pass
```

## API Endpoints

### Организации

| Метод | Път | Описание |
|-------|-----|----------|
| GET | `/organizations/` | Връща списък на организациите, в които потребителят членува. |
| POST | `/organizations/` | Създава нова организация (потребителят става неин `admin`). |
| GET | `/organizations/current` | Връща текущата активна организация. |
| GET | `/organizations/{id}` | Връща детайли за конкретна организация. |
| PUT | `/organizations/{id}` | Редактира данните на организацията (само за `admin`). |
| DELETE | `/organizations/{id}` | Изтрива организация (само за `admin`). |
| POST | `/organizations/{id}/switch` | Превключва активната организация за потребителя. |

### Членове

| Метод | Път | Описание |
|-------|-----|----------|
| GET | `/organizations/{id}/members` | Връща списък на членовете на организацията. |
| POST | `/organizations/{id}/members` | Добавя нов член към организацията (само за `admin`). |
| PUT | `/organizations/{id}/members/{user_id}` | Променя ролята на съществуващ член. |
| DELETE | `/organizations/{id}/members/{user_id}` | Премахва член от организацията. |

## Frontend

### `useOrganization` Hook

React hook, който осигурява лесен достъп до данните и функциите за управление на организациите:

```typescript
const {
  organizations,           // Списък с организациите на потребителя
  currentOrganization,     // Текущо избраната организация
  switchTo,               // Функция за превключване
  create,                 // Функция за създаване
  hasOrganizations,       // `true`, ако потребителят членува в поне една организация
  needsOrganization,      // `true`, ако потребителят трябва да създаде първата си организация
} = useOrganization()
```

### `OrganizationSwitcher` компонент

Компонент в потребителския интерфейс (обикновено в страничната лента), който позволява:
- Показване на името на текущата организация.
- Бързо превключване между различните организации.
- Бутон за създаване на нова организация.

## Миграция на базата данни

За да приложите необходимите промени в схемата на базата данни и да активирате многонаемната архитектура, изпълнете следната команда:

```bash
cd backend
alembic upgrade head
```

## Примери за употреба

### Създаване на организация (Frontend)

```typescript
const { create } = useOrganization()

create({
  name: "Моята фирма",
  slug: "moiata-firma"
})
```

### Превключване между организации (Frontend)

```typescript
const { switchTo } = useOrganization()

switchTo(organizationId)
```

### API заявка за създаване на обект (Backend)

Пример, който показва как `CurrentOrganization` и `CurrentUser` се използват за автоматично задаване на `organization_id` и `created_by_id` при създаване на нов артикул (`Item`).

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
