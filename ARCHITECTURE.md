# Barasurya ERP - Архитектура на проекта

## Структура на папките

```
barasurya-master/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── alembic/           # Database migrations
│   │   │   └── versions/      # Migration файлове
│   │   ├── api/
│   │   │   ├── deps.py        # Dependencies (auth, session, org)
│   │   │   ├── main.py        # API router registration
│   │   │   └── routes/        # API endpoints
│   │   ├── core/              # Core config, security, db
│   │   ├── crud/              # CRUD base class
│   │   ├── models/            # SQLModel models + Pydantic schemas
│   │   ├── services/          # Business logic services
│   │   └── utils.py           # Utility functions
│   └── pyproject.toml
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── client/            # Auto-generated API client
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── i18n/              # Internationalization (bg, en)
│   │   └── routes/            # TanStack Router pages
│   └── package.json
├── docs/                       # Documentation
└── docker-compose.yml         # Docker services
```

---

## База данни - Модели

### Основни модули

| Модул | Таблици | Описание |
|-------|---------|----------|
| **Организации** | `organization`, `organization_member` | Multi-tenant архитектура |
| **Потребители** | `user`, `role`, `permission`, `role_permission`, `user_role` | Аутентикация и права |
| **Контрагенти** | `contraagent`, `contraagent_bank_account`, `contact` | Клиенти/Доставчици (унифицирани) |
| **Стари клиенти** | `customer`, `customer_type`, `supplier` | Legacy модели (ще се мигрират) |

### Продукти и инвентар

| Модул | Таблици | Описание |
|-------|---------|----------|
| **Артикули (legacy)** | `item`, `item_category`, `item_unit` | Стара система за артикули |
| **Продукти (нов)** | `products`, `measurement_units`, `product_units` | Нова система от CyberERP |
| **Складове** | `store` | Магазини/Складове (STORE = СКЛАД!) |
| **Складови наличности** | `stock_levels`, `stock_movements`, `lots` | Следене на количества |
| **Складови операции** | `stock_adjustment`, `stock_transfer` | Корекции и трансфери |

### Документи - Покупки

| Модул | Таблици | Статуси | Описание |
|-------|---------|---------|----------|
| **Поръчки за доставка** | `purchase_orders`, `purchase_order_lines` | draft → sent → confirmed → received | Поръчки към доставчици |
| **Покупки** | `purchase`, `purchase_item` | - | Заприходяване на стоки |
| **Връщания** | `purchase_return`, `purchase_return_item` | - | Връщане към доставчик |

### Документи - Продажби

| Модул | Таблици | Статуси | Описание |
|-------|---------|---------|----------|
| **Оферти** | `quotations`, `quotation_lines` | draft → sent → accepted/rejected → converted | Оферти към клиенти |
| **Продажби** | `sale`, `sale_item` | - | Продажби на стоки |
| **Връщания** | `sale_return`, `sale_return_item` | - | Връщане от клиент |

### Финанси

| Модул | Таблици | Описание |
|-------|---------|----------|
| **Сметки** | `account`, `account_transaction` | Счетоводен сметкоплан |
| **Журнал** | `journal_entry`, `entry_line` | Счетоводни записи |
| **Плащания** | `payment`, `payable`, `receivable` | Парични операции |
| **Банки** | `bank_account`, `bank_transaction`, `bank_statement`, `bank_import`, `bank_profile` | Банкова интеграция |
| **Валути** | `currencies`, `exchange_rates` | Валути и курсове (ECB) |

### ДДС и отчетност

| Модул | Таблици | Описание |
|-------|---------|----------|
| **ДДС** | `vat_return`, `vat_sales_register`, `vat_purchase_register` | ДДС дневници и декларации |
| **Фактури** | `invoice`, `invoice_line` | Издадени фактури |
| **SAF-T** | `saft_*` таблици | Справки за НАП |

### Производство

| Модул | Таблици | Описание |
|-------|---------|----------|
| **Рецепти** | `recipe`, `recipe_item` | Производствени рецепти |

### Дълготрайни активи

| Модул | Таблици | Описание |
|-------|---------|----------|
| **Активи** | `asset`, `asset_transaction`, `asset_depreciation_schedule` | ДМА и амортизации |

---

## API Endpoints

### Регистрирани routes в `/api/v1/`

```
accounts/           - Счетоводни сметки
assets/             - Дълготрайни активи
bank-accounts/      - Банкови сметки
bank-transactions/  - Банкови транзакции
contraagents/       - Контрагенти (клиенти + доставчици)
currencies/         - Валути и курсове
customers/          - Клиенти (legacy)
customer_types/     - Типове клиенти
items/              - Артикули (legacy)
item_categories/    - Категории артикули
item_units/         - Мерни единици
login/              - Аутентикация
organizations/      - Организации
payments/           - Плащания
permissions/        - Права
purchase-orders/    - Поръчки за доставка (НОВ)
purchases/          - Покупки
quotations/         - Оферти (НОВ)
recipes/            - Рецепти
saft/               - SAF-T експорт
sales/              - Продажби
stock_levels/       - Складови наличности
stores/             - Магазини/Складове
suppliers/          - Доставчици (legacy)
users/              - Потребители
```

---

## Workflow на документи

### Поръчка за доставка (Purchase Order)

```
┌─────────┐     ┌──────┐     ┌───────────┐     ┌──────────┐     ┌────────┐
│  DRAFT  │ ──► │ SENT │ ──► │ CONFIRMED │ ──► │ RECEIVED │ ──► │ CLOSED │
└─────────┘     └──────┘     └───────────┘     └──────────┘     └────────┘
     │                             │                 │
     │                             │                 ▼
     ▼                             ▼          ┌──────────────────┐
┌───────────┐               ┌───────────┐     │ PARTIALLY_RECEIVED│
│ CANCELLED │               │ CANCELLED │     └──────────────────┘
└───────────┘               └───────────┘
```

### Оферта (Quotation)

```
┌─────────┐     ┌──────┐     ┌──────────┐     ┌─────────────────────┐
│  DRAFT  │ ──► │ SENT │ ──► │ ACCEPTED │ ──► │ CONVERTED_TO_INVOICE│
└─────────┘     └──────┘     └──────────┘     └─────────────────────┘
                    │              │
                    ▼              │
               ┌──────────┐        │
               │ REJECTED │        │
               └──────────┘        │
                    │              │
                    ▼              ▼
               ┌─────────┐    ┌─────────┐
               │ EXPIRED │    │CANCELLED│
               └─────────┘    └─────────┘
```

---

## Номериране на документи

Организацията пази следващите номера в полета:

```
sales_invoice_next_number       # Фактури продажба
purchase_invoice_next_number    # Фактури покупка
purchase_order_next_number      # Поръчки за доставка
quotation_next_number           # Оферти
credit_note_next_number         # Кредитни известия
debit_note_next_number          # Дебитни известия
stock_transfer_next_number      # Трансфери
stock_adjustment_next_number    # Корекции
proforma_invoice_next_number    # Проформи
vat_protocol_next_number        # ДДС протоколи
```

Формат: `PO0000000001`, `QT0000000001`, etc.

---

## Multi-tenant архитектура

```
┌──────────────────────────────────────────────────────────┐
│                         User                             │
└──────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────┐
│                  OrganizationMember                       │
│  (user_id, organization_id, role: owner/admin/manager/   │
│   accountant/member)                                      │
└──────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────┐
│                     Organization                          │
│  (всички данни са филтрирани по organization_id)         │
└──────────────────────────────────────────────────────────┘
```

Всяка таблица с данни има `organization_id` foreign key!

---

## Важни зависимости (Dependencies)

```python
# backend/app/api/deps.py

SessionDep          # Database session
CurrentUser         # Текущ логнат потребител
CurrentOrganization # Текуща избрана организация
CurrentMembership   # Членство на потребителя в организацията
RequireManager      # Изисква manager+ роля
```

---

## Конвенции за код

### Models (backend/app/models/)

```python
# Всеки файл съдържа:
class XxxBase(BaseModel):      # Базови полета
class Xxx(XxxBase, table=True): # Database model
class XxxCreate(XxxBase):       # Create schema
class XxxUpdate(SQLModel):      # Update schema (optional fields)
class XxxPublic(XxxBase):       # Response schema
class XxxsPublic(BaseModel):    # List response с count
```

### Routes (backend/app/api/routes/)

```python
# Всеки endpoint получава:
session: SessionDep              # DB session
current_org: CurrentOrganization # Текуща организация
membership: CurrentMembership    # Роля на потребителя
current_user: CurrentUser        # (при create) За created_by_id
```

---

## TODO / Незавършено

- [ ] `warehouse` модела НЕ се използва - `store` е склада!
- [ ] `invoices` таблицата не съществува - FK са деактивирани в PurchaseOrder и Quotation
- [ ] Миграция на `customer`/`supplier` към `contraagent`
- [ ] Миграция на `item` към `product`
- [ ] Frontend за `purchase-orders` и `quotations`
- [ ] Интеграция на Quotation → Invoice конвертиране

---

## Docker услуги

```yaml
services:
  db:         # PostgreSQL 17
  backend:    # FastAPI (port 8000)
  frontend:   # React/Vite (port 5173)
  proxy:      # Traefik
  adminer:    # DB admin (port 8080)
  mailcatcher: # Email testing (port 1080)
```

---

## Бързи команди

```bash
# Rebuild backend
docker compose up -d --build backend

# View logs
docker compose logs backend --tail 50

# Database shell
docker compose exec db psql -U barasurya -d barasurya_erp

# Run migrations
docker compose exec backend alembic upgrade head

# Generate frontend client
cd frontend && npm run generate-client
```
