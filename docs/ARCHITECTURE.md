# Barasurya ERP - Архитектурна документация

## Преглед

Barasurya ERP е модерна, мулти-тенант ERP система, разработена с FastAPI (Python) за бекенда и React (TypeScript) за фронтенда. Системата е специализирана за българския пазар с пълна ДДС съвместимост, SAF-T отчети и интрастат интеграция.

## Технологичен стек

### Бекенд (FastAPI)
- **FastAPI 0.115.6+** - Модерен async уеб фреймуърк
- **SQLModel 0.0.22** - Pydantic + SQLAlchemy интеграция
- **PostgreSQL 17** - Основна база данни
- **Alembic** - Database миграции
- **Pydantic v2** - Data validation и serialization
- **JWT** - Автентикация с токени
- **Bcrypt** - Password hashing
- **ECB Integration** - Европейска централна банка за валутни курсове

### Фронтенд (React)
- **React 18.3.1** - UI фреймуърк
- **TypeScript 5.7.2** - Type safety
- **TanStack Router 1.19.1** - Модерен routing с файлова структура
- **TanStack Query 5.62.7** - Server state management
- **Chakra UI 2.8.2** - Component библиотека
- **React Hook Form 7.54.1** - Form handling
- **i18next** - Интернационализация (BG/EN)

### Инфраструктура
- **Docker & Docker Compose** - Контейнеризация
- **Nginx** - Reverse proxy и static files
- **Traefik** - Load balancer за production
- **Redis** - Кеширане и сесии
- **PostgreSQL 17** - Primary database

## Архитектурни принципи

### 1. Мулти-тенант архитектура

Пълна изолация на данните между организации:

```python
# Всеки бизнес модел има organization_id
class Invoice(SQLModel, table=True):
    id: uuid.UUID
    organization_id: uuid.UUID  # Задължителен филтър
    # ... други полета
```

**API ниво:**
```python
@router.get("/invoices")
def get_invoices(
    current_org: CurrentOrganization,  # Автоматичен филтър
    session: SessionDep
):
    return session.exec(
        select(Invoice).where(Invoice.organization_id == current_org.id)
    )
```

**Фронтенд ниво:**
```typescript
// Организационен контекст
const { currentOrganization, switchTo } = useOrganization()
```

### 2. Ролева базирана сигурност (RBAC)

**Йерархия на ролите:**
- **ADMIN** - Пълен достъп до организацията
- **MANAGER** - Бизнес операции и CRUD
- **MEMBER** - Четене и базови операции

**API защита:**
```python
@router.delete("/invoices/{id}")
def delete_invoice(
    _: RequireAdmin,  # Само администратори
    session: SessionDep,
    invoice_id: uuid.UUID
):
    # Логика за изтриване
```

### 3. UUID-first дизайн

Всички първични ключове са UUID за distributed съвместимост:

```python
class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_updated: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
```

## База данни архитектура

### Схема на данните

**Основни таблици:**
- **organizations** - Мулти-тенант ядро
- **users** - Потребители и автентикация
- **organization_members** - Роли и членства
- **contraagents** - Обединени клиенти/доставчици
- **products** - Нов продуктова система от CyberERP
- **documents** - Фактури, поръчки, оферти
- **financial** - Сметки, плащания, ДДС
- **assets** - Дълготрайни активи и амортизация

### Моделни патерни

**1. Base Model Pattern:**
```python
class XxxBase(BaseModel):
    # Общи полета
    
class Xxx(XxxBase, table=True):
    # Database model
    
class XxxCreate(XxxBase):
    # Create schema
    
class XxxUpdate(SQLModel):
    # Update schema
    
class XxxPublic(XxxBase):
    # Response schema
    
class XxxsPublic(BaseModel):
    # List response с count
```

**2. Audit Trail:**
```python
class AuditLog(SQLModel, table=True):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    action: str
    resource: str
    resource_id: uuid.UUID
    old_values: dict
    new_values: dict
    ip_address: str
    user_agent: str
    timestamp: datetime
```

## API архитектура

### RESTful дизайн

**Base URL:**
```
Production: https://api.barasurya.com/v1
Development: http://localhost:8000/v1
```

**Стандартни endpoints:**
```
/api/v1/
├── accounts/           # Счетоводен план
├── assets/             # Дълготрайни активи
├── bank-accounts/      # Банкови сметки
├── contraagents/       # Клиенти/Доставчици
├── currencies/         # Валути
├── organizations/      # Мулти-тенант управление
├── payments/           # Плащания
├── purchase-orders/    # Поръчки за доставка
├── quotations/        # Оферти
├── saft/              # SAF-T отчети
├── sales/             # Продажби
├── stores/             # Складове
└── users/              # Потребители
```

### Dependency Injection

**Ключови зависимости:**
```python
SessionDep          # Database сесия
CurrentUser         # Аутентикиран потребител
CurrentOrganization # Мулти-тенант контекст
CurrentMembership   # Роля в организацията
RequireAdmin        # Admin достъп
RequireManager      # Manager достъп
```

### Auto-generated API Client

**OpenAPI интеграция:**
```typescript
// Автоматично генериран клиент
import { api } from '@/client'

// Type-safe API заявки
const invoices = await api.GET('/invoices', {
  params: {
    query: { status: 'issued', limit: 50 }
  }
})
```

## Фронтенд архитектура

### Component структура

```
src/
├── client/            # Auto-generated API клиент
├── components/        # React компоненти
│   ├── ui/           # Базови UI компоненти
│   ├── forms/        # Form компоненти
│   └── layouts/      # Layout компоненти
├── hooks/             # Custom React hooks
├── routes/            # TanStack Router страници
├── i18n/              # Интернационализация
└── utils.ts           # Utility функции
```

### File-based routing

```
src/routes/
├── _layout.tsx         # Authenticated layout
├── _layout/           # Protected routes
│   ├── index.tsx      # Dashboard
│   ├── assets.tsx     # Активи
│   ├── contraagents.tsx # Контрагенти
│   └── settings.tsx   # Настройки
├── login.tsx          # Логин
└── signup.tsx         # Регистрация
```

### State management

**Custom hooks:**
```typescript
// Автентикация
const { user, login, logout } = useAuth()

// Организации
const { organizations, currentOrganization, switchTo } = useOrganization()

// Toast notifications
const toast = useCustomToast()
```

## Бизнес логика и услуги

### Core Services

**1. DocumentNumberingService:**
```python
class DocumentNumberingService:
    def generate_number(
        self,
        organization_id: uuid.UUID,
        document_type: str,
        session: Session
    ) -> str:
        # Atomic номериране с database locking
```

**2. DocumentWorkflowService:**
```python
class DocumentWorkflowService:
    def transition(
        self,
        document: Document,
        new_status: str,
        user: User,
        session: Session
    ) -> Document:
        # Workflow преходи с audit trail
```

**3. SAFT Service:**
```python
class SAFTService:
    def generate_saft_xml(
        self,
        organization_id: uuid.UUID,
        period: str,
        session: Session
    ) -> str:
        # SAF-T XML генерация за НАП
```

**4. ECB Service:**
```python
class ECBService:
    def get_exchange_rates(self) -> dict:
        # Автоматично обновяване от Европейска централна банка
```

## Сигурност

### Автентикация

**JWT токени:**
```python
{
    "sub": "user_id",
    "exp": 1234567890,
    "iat": 1234567890
}
```

**Refresh токени:**
- Secure, HttpOnly cookies
- Rotation на всеки refresh
- Device fingerprinting

### Авторизация

**Ролева базирана сигурност:**
```python
def check_permission(
    user_role: str,
    required_permission: str,
    resource_owner_id: uuid.UUID = None
) -> bool:
    # Проверка на права с йерархия
```

**Организационна изолация:**
- Всички заявки филтрирани по organization_id
- Невъзможност за cross-organization достъп
- Automatic data leakage защита

## Производителност

### Database оптимизация

**Индексиране:**
```sql
-- Композитни индекси за мулти-тенант заявки
CREATE INDEX idx_organization_resource ON invoices(organization_id, date_created);
CREATE INDEX idx_organization_customer ON invoices(organization_id, customer_id);
CREATE INDEX idx_organization_status ON purchase_orders(organization_id, status);
```

**Connection pooling:**
- Async connection pool
- Connection reuse
- Health checks

### Кеширане

**Redis кеширане:**
```python
# Мулти-тенант кеш ключове
cache_key = f"org_{organization_id}:{resource}:{id}"

# Примери
"org_a1b2c3d4:customer:e5f6g7h8"
"org_a1b2c3d4:product_list:page_1"
```

### Frontend оптимизация

**Code splitting:**
```typescript
// Lazy loading на компоненти
const AssetsPage = lazy(() => import('./routes/assets'))
```

**Data caching:**
```typescript
// TanStack Query кеширане
const { data: invoices } = useQuery({
  queryKey: ['invoices', { status: 'issued' }],
  queryFn: () => api.GET('/invoices'),
  staleTime: 5 * 60 * 1000, // 5 минути
})
```

## Интеграции

### Външни системи

**1. Европейска централна банка (ECB):**
- Автоматично обновяване на валутни курсове
- Daily synchronization
- Historical rates

**2. НАП (Национална агенция за приходите):**
- SAF-T XML генерация
- ДДС декларации
- Интрастат отчети

**3. Банкови интеграции:**
- IBAN валидация
- Transaction imports
- Payment processing

### API интеграции

**Webhooks:**
```json
{
    "event": "invoice.created",
    "timestamp": "2025-01-14T10:30:00Z",
    "organization_id": "uuid",
    "data": {
        "id": "uuid",
        "invoice_no": "ИН0000000001",
        "total_amount": 1200.00
    }
}
```

## Deployment архитектура

### Docker Compose

**Services:**
```yaml
services:
  db:           # PostgreSQL 17
  backend:      # FastAPI (port 8000)
  frontend:     # React/Nginx (port 80)
  adminer:      # DB admin (port 8080)
  mailcatcher:  # Email testing (port 1080)
  prestart:     # Database initialization
```

### Production deployment

**Traefik configuration:**
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.barasurya.rule=Host(`barasurya.com`)"
  - "traefik.http.routers.barasurya.tls=true"
  - "traefik.http.routers.barasurya.tls.certresolver=letsencrypt"
```

## Мониторинг и логване

### Структурирано логване

```python
{
    "timestamp": "2025-01-14T10:30:45Z",
    "level": "INFO",
    "organization_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "user_id": "f6e5d4c3-b2a1-9876-5432-1fedcba987654",
    "action": "create_invoice",
    "resource": "invoice",
    "duration_ms": 150,
    "status": "success"
}
```

### Метрики

**Application метрики:**
- API response times
- Database query performance
- Error rates
- User activity
- Resource usage

**Business метрики:**
- Document creation rates
- User engagement
- Feature adoption
- Compliance rates

## Тестване

### Backend тестване

**Pytest структура:**
```python
# Unit тестове
def test_document_numbering_service():
    # Тест на бизнес логика

# Integration тестове
def test_create_invoice_api():
    # Тест на API endpoint

# E2E тестове
def test_invoice_workflow():
    # Тест на цял workflow
```

### Frontend тестване

**Playwright E2E:**
```typescript
test('user can create invoice', async ({ page }) => {
  await page.goto('/invoices/new')
  await page.fill('[data-testid="customer-select"]', 'Test Customer')
  await page.click('[data-testid="save-button"]')
  await expect(page.locator('[data-testid="success-toast"]')).toBeVisible()
})
```

## Миграция и съвместимост

### От CyberERP към FastAPI

**Основни подобрения:**
- UUID първични ключове (спрямо integer IDs)
- Async/await архитектура (спрямо GenServer)
- RESTful API (спрямо Phoenix/GraphQL)
- Static typing (спрямо dynamic)
- Modern tooling и CI/CD

**Запазени концепции:**
- Document numbering система
- Workflow patterns
- Multi-tenancy
- VAT съвместимост
- Business logic правила

## Бъдещи развития

### Краткосрочни (Q1 2025)
- Price List Management
- Advanced Inventory Features
- Document Forms и Validation
- Performance Optimization

### Средносрочни (Q2-Q3 2025)
- Manufacturing Module
- Real-time Features
- AI/ML Integration
- Mobile Applications

### Дългосрочни (Q4 2025+)
- Microservices Architecture
- Enterprise Features
- Global Expansion
- Advanced Analytics

## Най-добри практики

### Code организация
- Clear separation of concerns
- Consistent naming conventions
- Type safety throughout
- Comprehensive error handling

### Сигурност
- Principle of least privilege
- Regular security audits
- Data encryption
- Secure coding practices

### Производителност
- Efficient database queries
- Proper indexing
- Caching strategies
- Load testing

### Поддръжка
- Comprehensive monitoring
- Automated testing
- Documentation
- Disaster recovery planning

## Заключение

Barasurya ERP представлява модерна, добре архитектурирана система, която съчетава най-добрите практики от contemporary software development с дълбоко разбиране на българския бизнес контекст. Архитектурата е проектирана за скалируемост, сигурност и лесна поддръжка, като същевременно предоставя богата функционалност за управление на бизнес процеси.