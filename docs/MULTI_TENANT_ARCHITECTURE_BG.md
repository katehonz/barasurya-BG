# Мулти-тенант архитектура и организация

## Преглед

Мулти-тенант архитектурата позволява на една инсталация на системата да обслужва множество организации (тенанти), като същевременно гарантира пълна изолация на данните, персонализирани настройки и сигурност. Всяка организация работи в независима среда със собствени данни, конфигурации и потребители.

## Архитектурни принципи

### 1. Изолация на данните

Пълна изолация на данните между различните организации:

#### База данни ниво:
- Всеки запис има `organization_id` поле
- Всички заявки включат филтър по организация
- Невъзможност за достъп до чужди данни

#### API ниво:
- Автоматично филтриране по организация
- Валидация на достъпа на ниво middleware
- Проверка на права за достъп

#### UI ниво:
- Само данни от текущата организация
- Изолирани потребителски сесии
- Организационен контекст

### 2. Споделени ресурси

Ефективно споделяне на ресурси:

#### Изчислителни ресурси:
- Споделени сървърни ресурси
- Оптимизирана употреба на памет
- Load balancing

#### Сървиси:
- Споделени бизнес логики
- Общи валидации
- Централизирани услуги

#### Инфраструктура:
- Една база данни
- Споделени файлове
- Централизиран backup

### 3. Персонализация

Всяка организация има индивидуални настройки:

#### Бизнес настройки:
- Собствени документни номерации
- Конфигурируеми ДДС ставки
- Персонализирани работни процеси
- Собствени справочници

#### Визуални настройки:
- Лого и брандинг
- Цветове и теми
- Персонализирани полета
- Собствени отчети

## Организационна структура

### 1. Организация (Organization)

Основната единица в мулти-тенант архитектурата:

#### Основни полета:
```python
class Organization:
    id: UUID                    # Уникален идентификатор
    name: str                   # Име на организацията
    slug: str                   # URL дружелюбен идентификатор
    eik: str                    # ЕИК/БУЛСТАТ
    is_active: bool              # Активна ли е организацията
    region_code: str            # Регионен код
    default_currency_code: str   # Дефолтна валута
    base_currency_id: UUID       # Основна валута
    tax_basis: str              # Основа за облагане
    in_eurozone: bool           # Дали е в Еврозоната
```

#### Счетоводни настройки:
```python
# Сметков план
accounts_receivable_account_id: UUID      # Сметка 41
sales_revenue_account_id: UUID           # Сметка 701
vat_payable_account_id: UUID              # Сметка 4531
inventory_account_id: UUID               # Сметка 301
accounts_payable_account_id: UUID         # Сметка 401
vat_deductible_account_id: UUID           # Сметка 4532
cash_account_id: UUID                    # Сметка 501
```

#### Документни номерации:
```python
# Последващи номера за документи
sales_invoice_next_number: int           # Фактури
purchase_invoice_next_number: int        # Фактури от доставчици
purchase_order_next_number: int          # Поръчки за доставка
quotation_next_number: int               # Оферти
credit_note_next_number: int             # Кредитни известия
debit_note_next_number: int              # Дебитни известия
stock_transfer_next_number: int         # Складови трансфери
stock_adjustment_next_number: int       # Складови корекции
proforma_invoice_next_number: int        # Проформа фактури
vat_protocol_next_number: int           # ДДС протоколи
```

### 2. Потребители и роли

#### Потребители (Users):
```python
class User:
    id: UUID                    # Уникален идентификатор
    email: str                  # Имейл (уникален в системата)
    full_name: str              # Пълно име
    is_active: bool            # Активен ли е потребителят
    is_superuser: bool          # Супер потребител
    hashed_password: str       # Хеширана парола
```

#### Членство в организация (OrganizationMember):
```python
class OrganizationMember:
    id: UUID                    # Уникален идентификатор
    organization_id: UUID       # Организация
    user_id: UUID              # Потребител
    role_id: UUID              # Роля
    is_active: bool            # Активен ли е членството
    date_joined: datetime       # Дата на присъединяване
```

#### Роли (Roles):
```python
class Role:
    id: UUID                    # Уникален идентификатор
    organization_id: UUID       # Организация
    name: str                  # Име на ролята
    description: str            # Описание
    is_system: bool            # Системна роля
```

#### Права (Permissions):
```python
class Permission:
    id: UUID                    # Уникален идентификатор
    name: str                  # Име на правото
    resource: str              # Ресурс (invoice, customer, etc.)
    action: str                # Действие (create, read, update, delete)
    description: str          # Описание
```

### 3. Йерархия на ролите

#### Стандартни роли:
- **Супер администратор** - Пълен достъп до всички организации
- **Администратор** - Пълен достъп до собствената организация
- **Мениджър** - Достъп до всички модули в организацията
- **Счетоводител** - Достъп до счетоводни модули
- **Складов работник** - Достъп до складови модули
- **Търговец** - Достъп до продажби и клиенти
- **Оператор** - Ограничен достъп за основни операции

#### Персонализирани роли:
- Възможност за създаване на персонализирани роли
- Комбиниране на различни права
- Ограничаване на достъпа по модули

## Сигурност

### 1. Автентикация

#### JWT токени:
```python
{
    "sub": "user_id",           # Subject (потребител)
    "org": "organization_id",   # Организация
    "role": "role_name",        # Роля
    "exp": 1234567890,         # Expiration
    "iat": 1234567890          # Issued at
}
```

#### Мулти-тенант сесии:
- Един потребител може да има достъп до множество организации
- Превключване между организации без ново логване
- Контекст на текущата организация

### 2. Авторизация

#### Ролева базирана сигурност (RBAC):
- Проверка на права на ниво ресурс
- Йерархични роли
- Динамични права

#### Организационна изолация:
- Автоматично филтриране по организация
- Проверка на достъпа на ниво middleware
- Защита от data leakage

### 3. Audit Trail

#### Логване на операции:
```python
class AuditLog:
    id: UUID                    # Уникален идентификатор
    organization_id: UUID       # Организация
    user_id: UUID              # Потребител
    action: str                # Действие
    resource: str              # Ресурс
    resource_id: UUID          # ID на ресурса
    old_values: dict           # Стари стойности
    new_values: dict           # Нови стойности
    ip_address: str            # IP адрес
    user_agent: str           # User agent
    timestamp: datetime        # Време на операцията
```

## Конфигурация

### 1. Организационни настройки

#### Бизнес настройки:
- Работно време и почивни дни
- Валутни курсове
- ДДС ставки
- Счетоводен план
- Работни процеси

#### Технически настройки:
- Email конфигурация
- Backup настройки
- Интеграционни ключове
- API лимити

### 2. Персонализация

#### Брандинг:
```python
class Branding:
    organization_id: UUID       # Организация
    logo_url: str             # Лого
    primary_color: str        # Основен цвят
    secondary_color: str      # Вторичен цвят
    font_family: str          # Шрифт
    custom_css: str          # Персонализиран CSS
```

#### Персонализирани полета:
```python
class CustomField:
    id: UUID                    # Уникален идентификатор
    organization_id: UUID       # Организация
    resource: str              # Ресурс (customer, product, etc.)
    field_name: str            # Име на полето
    field_type: str            # Тип (text, number, date, etc.)
    is_required: bool          # Задължително ли е
    default_value: str         # Стойност по подразбиране
```

## Производителност

### 1. Оптимизация на базата данни

#### Индексиране:
```sql
-- Композитни индекси за мулти-тенант заявки
CREATE INDEX idx_organization_resource ON invoices(organization_id, date_created);
CREATE INDEX idx_organization_customer ON invoices(organization_id, customer_id);
CREATE INDEX idx_organization_status ON purchase_orders(organization_id, status);
```

#### Partitioning:
- Partitioning по организация за големи таблици
- Автоматично управление на partitions
- Оптимизирани заявки

### 2. Кеширане

#### Мулти-тенант кеш:
```python
# Кеш ключове с организация
cache_key = f"org_{organization_id}:{resource}:{id}"

# Примери
"org_a1b2c3d4:customer:e5f6g7h8"
"org_a1b2c3d4:product_list:page_1"
```

#### Redis кеширане:
- Разделяне на кеша по организации
- Автоматично изчистване
- TTL управление

### 3. Load Balancing

#### Хоризонтално скалиране:
- Множество application сървъри
- Load balancer с sticky sessions
- Автоматично разпределение

#### Database connection pooling:
- Connection pool по организация
- Оптимизиране на връзките
- Monitoring на производителността

## Мониторинг и поддръжка

### 1. Метрики

#### Организационни метрики:
- Брой активни организации
- Потребители по организации
- Обем на данни по организации
- API заявки по организации

#### Системни метрики:
- CPU и памет по организации
- Database performance
- Response times
- Error rates

### 2. Логване

#### Структурирано логване:
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

#### Централизирано логване:
- ELK stack (Elasticsearch, Logstash, Kibana)
- Real-time мониторинг
- Alerting

### 3. Backup и Recovery

#### Организационен backup:
```python
# Backup стратегия
daily_backup = {
    "full_backup": True,
    "organizations": "all",
    "retention": "30_days"
}

incremental_backup = {
    "full_backup": False,
    "organizations": "active",
    "retention": "7_days"
}
```

#### Disaster recovery:
- Geographic distribution
- Automated failover
- Point-in-time recovery
- Testing procedures

## Интеграции

### 1. API интеграции

#### Мулти-тенант API:
```python
# API endpoints с организация
GET /api/{organization_slug}/invoices
POST /api/{organization_slug}/customers
PUT /api/{organization_slug}/products/{id}

# Или с header
GET /api/invoices
Headers:
  X-Organization-ID: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
```

#### Webhooks:
- Организационни webhooks
- Персонализирани събития
- Сигурност с подписи

### 2. Трети страни интеграции

#### Плащания:
- Различни платежни провайдери по организации
- Персонализирани настройки
- Автоматично разпределение

#### Складови системи:
- ERP интеграции
- Real-time синхронизация
- Мулти-тенант mapping

## Бъдещи развития

### Планирани функционалности:
- Географска дистрибуция
- Advanced security features
- AI базирана оптимизация
- Real-time collaboration
- Mobile-first design

### Технологични подобрения:
- Microservices архитектура
- Event-driven architecture
- GraphQL API
- Serverless components
- Edge computing

## Най-добри практики

### 1. Дизайн
- Clear separation of concerns
- Consistent API design
- Proper error handling
- Comprehensive logging

### 2. Сигурност
- Principle of least privilege
- Regular security audits
- Data encryption
- Secure coding practices

### 3. Производителност
- Efficient database queries
- Proper indexing
- Caching strategies
- Load testing

### 4. Поддръжка
- Comprehensive monitoring
- Automated testing
- Documentation
- Disaster recovery planning