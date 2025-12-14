# Cyber ERP

**Система за управление на бизнес ресурси (ERP) на български език**

Модерна ERP система изградена с Elixir Phoenix, LiveView и React за сложни компоненти.

## Език на проекта

**Важно:** Този проект е на **български език**. Всички потребителски интерфейси, документация, коментари в кода и комуникация се водят на български.

## Технологии

### Backend
- **Elixir** - Функционален език за надеждни и мащабируеми приложения
- **Phoenix Framework** - Web framework с real-time възможности
- **Phoenix LiveView** - Server-side rendering с real-time updates
- **Ecto** - Database wrapper и query builder
- **PostgreSQL** - Релационна база данни

### Frontend
- **Phoenix LiveView** - За повечето UI компоненти (списъци, таблици, навигация)
- **React** - За сложни форми, rich text editors, интерактивни визуализации
- **Alpine.js** - За леки клиентски интерактивности
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - За графики и визуализации на данни

## Архитектура

Проектът използва **Модулен монолит** (Modular Monolith) архитектура с Phoenix Umbrella структура:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Cyber ERP (Модулен монолит)                  │
├─────────────────────────────────────────────────────────────────┤
│  Accounting │  Sales  │  Purchase  │  Inventory  │  Bank  │ ... │
├─────────────────────────────────────────────────────────────────┤
│                    Shared Kernel (Repo, PubSub)                  │
├─────────────────────────────────────────────────────────────────┤
│                       PostgreSQL Database                        │
└─────────────────────────────────────────────────────────────────┘

cyber_erp/
├── apps/
│   ├── cyber_core/      # Business logic, схеми, контексти
│   └── cyber_web/       # Web интерфейс (LiveView + React)
├── config/              # Конфигурация
└── deps/                # Зависимости
```

**Защо модулен монолит вместо микросервизи?**
- ACID транзакции между модули (критично за SAF-T)
- Простота на deployment (един Docker контейнер)
- BEAM платформата осигурява скалиране
- По-лесен debugging и мониторинг
- Ясен път към микросервизи при нужда

Повече: [Архитектура - Модулен монолит vs Микросервизи](docs/ARCHITECTURE_BG.md#модулен-монолит-защо-не-микросервизи)

### Хибриден подход: LiveView + React

**LiveView компоненти** (server-side):
- Списъци и таблици с данни
- Dashboard и отчети
- Навигация и layouts
- Real-time notifications

**React компоненти** (client-side):
- Сложни форми с много валидации
- Rich text editors
- Интерактивни графики (Recharts)
- Drag & drop интерфейси
- Autocomplete с много данни

Интеграцията става чрез LiveView hooks в `assets/js/app.js`.

## Модули

### ✅ Реализирани модули

1. **Accounts** - Потребители и организации
   - Multi-tenancy (Tenant)
   - Потребители и роли (User)

2. **Accounting** - Счетоводство и финансово управление
   - Сметкоплан (Account)
   - Дневници и записи (JournalEntry, JournalLine)
   - Активи и амортизация (Asset, AssetDepreciationSchedule)
   - Финансови сметки и транзакции

3. **Inventory** - Складово стопанство
   - Продукти (Product)
   - Складове (Warehouse)
   - Складови движения (StockMovement)
   - Наличности (StockLevel)

4. **Sales** - Продажби
   - Фактури (Invoice, InvoiceLine)
   - Оферти (Quotation, QuotationLine)
   - Продажби (Sale)

5. **Purchase** - Покупки
   - Поръчки за покупка (PurchaseOrder, PurchaseOrderLine)
   - Фактури от доставчици (SupplierInvoice, SupplierInvoiceLine)

6. **Bank** - Банкови операции
   - Банкови сметки (BankAccount)
   - Транзакции (BankTransaction)
   - Извлечения (BankStatement)

7. **Contacts** - CRM
   - Клиенти и доставчици (Contact)

8. **Authentication & Authorization** - Система за вход и права
   - Login/Logout
   - Session management
   - Role-based permissions (RBAC)
   - Permissions UI за superadmin
   - Multi-tenant support

9. **Document Processing** - AI обработка на документи ⭐ NEW
   - Azure Form Recognizer интеграция
   - Автоматично извличане на данни от PDF фактури
   - S3 Hetzner Storage за съхранение на документи
   - UI за upload на документи (drag & drop)
   - Преглед и одобрение на извлечени данни
   - Confidence scoring на AI резултати
   - Workflow: pending_review → approved/rejected

### 📚 Документация

За повече информация вижте директорията [docs/](docs/):
- 📖 [Архитектура](docs/ARCHITECTURE_BG.md) - Подробна документация за архитектурата
- 🔐 [Authentication & Authorization](docs/AUTHENTICATION.md) - Система за вход и права
- 🗺️ [Модулна диаграма](docs/MODULES_DIAGRAM_BG.md) - Визуализация на модулите
- 📋 [План за модули](docs/MODULES_PLAN.md) - Подробен план за миграция
- 🚀 [Бърз старт](docs/QUICK_START_BG.md) - Ръководство за разработчици
- 📊 [Състояние на проекта](docs/PROJECT_STATUS_BG.md) - Текущ прогрес
- 📝 [Резюме](docs/SUMMARY_BG.md) - Обобщение на проекта
- 🤖 [Azure Form Recognizer Setup](docs/AZURE_FORM_RECOGNIZER_SETUP.md) - AI обработка на документи
- 🏦 [Bank Profiles](docs/BANK_PROFILES.md) - Банкови профили и импорт
- 🔢 [Nomenclatures](docs/NOMENCLATURES.md) - КН номенклатура и мерни единици
- 💾 [Cache Quickstart](docs/CACHE_QUICKSTART.md) - ETS кеш система

## Стартиране

### Изисквания

- Elixir 1.14+
- Erlang/OTP 26+
- PostgreSQL 14+
- Node.js 18+ (за frontend assets)

### Setup

```bash
# Инсталиране на зависимости
mix deps.get

# Създаване на база данни и стартиране на seeds
mix ecto.setup

# Стартиране на сървъра (препоръчан метод)
./start.sh

# Или директно:
cd apps/cyber_web && mix phx.server
```

Приложението ще бъде достъпно на `http://localhost:4000`

### 🔐 Demo Потребители

След `mix ecto.setup` ще имате готови демо потребители:

| Роля | Email | Парола | Права |
|------|-------|--------|-------|
| **Superadmin** | `superadmin@example.com` | `password123` | Всички + управление на права |
| **Admin** | `admin@demo.com` | `password123` | Всички операции |
| **User** | `user@demo.com` | `password123` | Основни операции |
| **Observer** | `observer@demo.com` | `password123` | Само четене |

Повече информация: [Authentication Documentation](docs/AUTHENTICATION.md)

### API документация

API endpoints са достъпни на `/api`:

- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `GET /api/auth/me` - Текущ потребител
- `/api/contacts` - CRUD за контакти
- `/api/products` - CRUD за продукти
- `/api/sales` - CRUD за продажби
- `/api/accounting/*` - Счетоводни операции

## Разработка

### Структура на кода

- Всички модели и business logic са в `apps/cyber_core/lib/cyber_core/`
- Web контролери и LiveView са в `apps/cyber_web/lib/cyber_web/`
- React компоненти ще бъдат в `apps/cyber_web/assets/js/components/`
- Стилове са в `apps/cyber_web/assets/css/`

### Тестване

```bash
mix test
```

### База данни

```bash
# Миграции
mix ecto.migrate

# Rollback
mix ecto.rollback

# Reset база данни
mix ecto.reset
```

## Multi-tenancy

Системата поддържа множество организации (tenants) чрез:
- `X-Tenant-ID` header за API заявки
- Автоматична изолация на данни per tenant
- Префикс на схемата в PostgreSQL

## Лиценз

Proprietary - Всички права запазени
