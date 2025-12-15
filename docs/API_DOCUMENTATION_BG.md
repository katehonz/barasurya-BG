# API документация и интеграция

## Преглед

API документацията описва всички налични ендпойнти за интеграция със системата за управление на документи, складови операции и ДДС съвместимост. API-то следва RESTful принципи и използва JSON формат за обмен на данни.

## Базова информация

### Base URL
```
Production: https://api.barasurya.com/v1
Development: http://localhost:8000/api/v1
```

### Аутентикация
API-то използва JWT (JSON Web Tokens) за автентикация:

```http
Authorization: Bearer <jwt_token>
```

### Организационен контекст
Всички заявки изискват организационен контекст:

```http
# Метод 1: URL параметър
GET /v1/organizations/{org_slug}/invoices

# Метод 2: Header
GET /v1/invoices
X-Organization-ID: {organization_id}
```

## Стандартни отговори

### Успешни отговори

#### 200 OK
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "Име на ресурса"
    }
}
```

#### 201 Created
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "Име на ресурса"
    },
    "message": "Ресурсът е създаден успешно"
}
```

#### 204 No Content
```json
{
    "success": true,
    "message": "Операцията е изпълнена успешно"
}
```

### Грешки

#### 400 Bad Request
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Невалидни данни",
        "details": {
            "field_name": ["Полето е задължително"]
        }
    }
}
```

#### 401 Unauthorized
```json
{
    "success": false,
    "error": {
        "code": "UNAUTHORIZED",
        "message": "Невалидна автентикация"
    }
}
```

#### 403 Forbidden
```json
{
    "success": false,
    "error": {
        "code": "FORBIDDEN",
        "message": "Нямате права за тази операция"
    }
}
```

#### 404 Not Found
```json
{
    "success": false,
    "error": {
        "code": "NOT_FOUND",
        "message": "Ресурсът не е намерен"
    }
}
```

#### 500 Internal Server Error
```json
{
    "success": false,
    "error": {
        "code": "INTERNAL_ERROR",
        "message": "Вътрешна грешка на сървъра"
    }
}
```

## Пагинация

Всички списъчни ендпойнти поддържат пагинация:

### Query параметри
```
GET /v1/invoices?page=1&limit=20&sort=date_created&order=desc
```

- `page` - Номер на страницата (default: 1)
- `limit` - Брой записи на страница (default: 20, max: 100)
- `sort` - Поле за сортиране
- `order` - Ред на сортиране (asc/desc)

### Отговор с пагинация
```json
{
    "success": true,
    "data": [
        {"id": "uuid", "name": "Ресурс 1"},
        {"id": "uuid", "name": "Ресурс 2"}
    ],
    "pagination": {
        "page": 1,
        "limit": 20,
        "total": 150,
        "pages": 8,
        "has_next": true,
        "has_prev": false
    }
}
```

## Филтриране и търсене

### Основни филтри
```
GET /v1/invoices?status=issued&customer_id=uuid&date_from=2025-01-01&date_to=2025-01-31
```

### Търсене
```
GET /v1/customers?search=Име на клиент
```

### Разширено търсене
```json
POST /v1/invoices/search
{
    "filters": {
        "status": ["issued", "paid"],
        "customer_id": ["uuid1", "uuid2"],
        "total_amount": {
            "min": 100,
            "max": 1000
        }
    },
    "search": {
        "fields": ["invoice_no", "customer_name"],
        "query": "търсене"
    },
    "sort": [
        {"field": "date_created", "order": "desc"},
        {"field": "invoice_no", "order": "asc"}
    ]
}
```

## Фактури (Invoices)

### CRUD операции

#### Списък с фактури
```http
GET /v1/invoices
```

**Query параметри:**
- `status` - Статус на фактура (draft, issued, paid, etc.)
- `customer_id` - UUID на клиент
- `date_from` - Начална дата (YYYY-MM-DD)
- `date_to` - Крайна дата (YYYY-MM-DD)
- `vat_document_type` - Тип ДДС документ (01-96)

**Пример:**
```http
GET /v1/invoices?status=issued&date_from=2025-01-01&limit=50
```

#### Детайли за фактура
```http
GET /v1/invoices/{invoice_id}
```

**Отговор:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "invoice_no": "ИН0000000001",
        "status": "issued",
        "issue_date": "2025-01-14",
        "due_date": "2025-01-28",
        "customer": {
            "id": "uuid",
            "name": "Клиент ООД",
            "eik": "123456789"
        },
        "subtotal": 1000.00,
        "tax_amount": 200.00,
        "total_amount": 1200.00,
        "currency_code": "BGN",
        "vat_document_type": "01",
        "invoice_lines": [
            {
                "id": "uuid",
                "product_name": "Продукт 1",
                "quantity": 10,
                "unit_price": 100.00,
                "tax_rate": 20.00,
                "line_total": 1000.00,
                "tax_amount": 200.00
            }
        ]
    }
}
```

#### Нова фактура
```http
POST /v1/invoices
```

**Тяло на заявката:**
```json
{
    "issue_date": "2025-01-14",
    "due_date": "2025-01-28",
    "customer_id": "uuid",
    "billing_name": "Клиент ООД",
    "billing_address": "гр. София, ул. Васил Левски 1",
    "billing_vat_number": "BG123456789",
    "currency_code": "BGN",
    "vat_document_type": "01",
    "notes": "Бележки към фактурата",
    "invoice_lines": [
        {
            "product_id": "uuid",
            "quantity": 10,
            "unit_price": 100.00,
            "tax_rate": 20.00
        }
    ]
}
```

#### Редакция на фактура
```http
PUT /v1/invoices/{invoice_id}
```

#### Изтриване на фактура
```http
DELETE /v1/invoices/{invoice_id}
```

### Workflow операции

#### Издаване на фактура
```http
POST /v1/invoices/{invoice_id}/issue
```

**Отговор:**
```json
{
    "success": true,
    "message": "Фактурата е издадена успешно",
    "data": {
        "status": "issued",
        "date_issued": "2025-01-14T10:30:00Z"
    }
}
```

#### Анулиране на фактура
```http
POST /v1/invoices/{invoice_id}/cancel
```

**Тяло на заявката:**
```json
{
    "reason": "Причина за анулиране"
}
```

## Поръчки за доставка (Purchase Orders)

### CRUD операции

#### Списък с поръчки
```http
GET /v1/purchase-orders
```

**Query параметри:**
- `status` - Статус (draft, sent, confirmed, received)
- `supplier_id` - UUID на доставчик
- `warehouse_id` - UUID на склад
- `date_from` - Начална дата
- `date_to` - Крайна дата

#### Детайли за поръчка
```http
GET /v1/purchase-orders/{order_id}
```

**Отговор:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "order_no": "ПО0000000001",
        "status": "confirmed",
        "order_date": "2025-01-14",
        "expected_delivery_date": "2025-01-20",
        "supplier": {
            "id": "uuid",
            "name": "Доставчик АД"
        },
        "warehouse": {
            "id": "uuid",
            "name": "Основен склад"
        },
        "subtotal": 5000.00,
        "tax_amount": 1000.00,
        "total_amount": 6000.00,
        "currency_code": "BGN",
        "purchase_order_lines": [
            {
                "id": "uuid",
                "product_name": "Суровина 1",
                "quantity": 100,
                "unit_price": 50.00,
                "received_quantity": 0,
                "remaining_quantity": 100
            }
        ]
    }
}
```

#### Нова поръчка
```http
POST /v1/purchase-orders
```

**Тяло на заявката:**
```json
{
    "order_date": "2025-01-14",
    "expected_delivery_date": "2025-01-20",
    "supplier_id": "uuid",
    "warehouse_id": "uuid",
    "delivery_address": "гр. София, ул. Индустриална 1",
    "payment_terms": "30 дни от фактуриране",
    "notes": "Специални изисквания",
    "purchase_order_lines": [
        {
            "product_id": "uuid",
            "quantity": 100,
            "unit_price": 50.00,
            "tax_rate": 20.00
        }
    ]
}
```

### Workflow операции

#### Изпращане на поръчка
```http
POST /v1/purchase-orders/{order_id}/send
```

#### Потвърждаване на поръчка
```http
POST /v1/purchase-orders/{order_id}/confirm
```

#### Частично получаване
```http
POST /v1/purchase-orders/{order_id}/partial-receive
```

**Тяло на заявката:**
```json
{
    "lines": [
        {
            "line_id": "uuid",
            "received_quantity": 50
        }
    ],
    "notes": "Частично получаване"
}
```

## Оферти (Quotations)

### CRUD операции

#### Списък с оферти
```http
GET /v1/quotations
```

**Query параметри:**
- `status` - Статус (draft, sent, accepted, rejected)
- `customer_id` - UUID на клиент
- `valid_from` - Валидна от дата
- `valid_to` - Валидна до дата
- `probability_min` - Минимална вероятност
- `probability_max` - Максимална вероятност

#### Детайли за оферта
```http
GET /v1/quotations/{quotation_id}
```

**Отговор:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "quotation_no": "ОФ0000000001",
        "status": "sent",
        "quotation_date": "2025-01-14",
        "valid_until": "2025-01-31",
        "customer": {
            "id": "uuid",
            "name": "Клиент ООД"
        },
        "probability": 75.00,
        "subtotal": 2000.00,
        "tax_amount": 400.00,
        "total_amount": 2400.00,
        "currency_code": "BGN",
        "quotation_lines": [
            {
                "id": "uuid",
                "product_name": "Продукт 1",
                "quantity": 20,
                "unit_price": 100.00,
                "optional": false,
                "delivery_time": "14 дни"
            }
        ]
    }
}
```

#### Нова оферта
```http
POST /v1/quotations
```

**Тяло на заявката:**
```json
{
    "quotation_date": "2025-01-14",
    "valid_until": "2025-01-31",
    "customer_id": "uuid",
    "probability": 75.00,
    "payment_terms": "30 дни от фактуриране",
    "delivery_terms": "Доставка до адрес на клиента",
    "warranty_terms": "24 месеца гаранция",
    "quotation_lines": [
        {
            "product_id": "uuid",
            "quantity": 20,
            "unit_price": 100.00,
            "tax_rate": 20.00,
            "optional": false,
            "delivery_time": "14 дни"
        }
    ]
}
```

### Workflow операции

#### Изпращане на оферта
```http
POST /v1/quotations/{quotation_id}/send
```

#### Приемане на оферта
```http
POST /v1/quotations/{quotation_id}/accept
```

#### Отхвърляне на оферта
```http
POST /v1/quotations/{quotation_id}/reject
```

**Тяло на заявката:**
```json
{
    "rejection_reason": "Причина за отхвърляне"
}
```

#### Конвертиране във фактура
```http
POST /v1/quotations/{quotation_id}/convert-to-invoice
```

## Складови операции

### Продукти

#### Списък с продукти
```http
GET /v1/products
```

**Query параметри:**
- `category` - Категория (goods, materials, services, produced)
- `is_active` - Активен ли е продуктът
- `track_inventory` - Проследява ли се наличност
- `search` - Търсене по име или SKU

#### Детайли за продукт
```http
GET /v1/products/{product_id}
```

**Отговор:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "Продукт 1",
        "sku": "PROD001",
        "description": "Описание на продукта",
        "category": "goods",
        "price": 120.00,
        "cost": 80.00,
        "tax_rate": 20.00,
        "unit": "бр.",
        "barcode": "1234567890123",
        "is_active": true,
        "track_inventory": true,
        "stock_levels": [
            {
                "warehouse_id": "uuid",
                "warehouse_name": "Основен склад",
                "quantity": 500,
                "reserved_quantity": 50,
                "available_quantity": 450
            }
        ]
    }
}
```

### Складови нива

#### Наличности по складове
```http
GET /v1/stock-levels
```

**Query параметри:**
- `warehouse_id` - UUID на склад
- `product_id` - UUID на продукт
- `low_stock` - Само продукти с ниски наличности

#### Актуализиране на наличности
```http
PUT /v1/stock-levels/{level_id}
```

**Тяло на заявката:**
```json
{
    "quantity": 100,
    "reserved_quantity": 10,
    "notes": "Корекция на наличности"
}
```

### Складови движения

#### Списък с движения
```http
GET /v1/stock-movements
```

**Query параметри:**
- `movement_type` - Тип движение (in, out, transfer, adjustment)
- `warehouse_id` - UUID на склад
- `product_id` - UUID на продукт
- `date_from` - Начална дата
- `date_to` - Крайна дата

#### Ново движение
```http
POST /v1/stock-movements
```

**Тяло на заявката:**
```json
{
    "movement_type": "in",
    "warehouse_id": "uuid",
    "reference_type": "purchase_order",
    "reference_id": "uuid",
    "date_movement": "2025-01-14",
    "notes": "Приемане по поръчка",
    "stock_movement_lines": [
        {
            "product_id": "uuid",
            "quantity": 100,
            "unit_cost": 80.00
        }
    ]
}
```

## ДДС и справки

### ДДС регистри

#### Продажби
```http
GET /v1/vat/sales-register
```

**Query параметри:**
- `date_from` - Начална дата
- `date_to` - Крайна дата
- `vat_document_type` - Тип документ
- `customer_vat_number` - ДДС номер на клиент

#### Придобивания
```http
GET /v1/vat/purchase-register
```

### ДДС декларация

#### Генериране на декларация
```http
POST /v1/vat/declaration
```

**Тяло на заявката:**
```json
{
    "period": "2025-01",
    "type": "monthly"
}
```

**Отговор:**
```json
{
    "success": true,
    "data": {
        "declaration_id": "uuid",
        "period": "2025-01",
        "section_1": {
            "line_1": 10000.00,
            "line_2": 2000.00,
            "line_3": 5000.00,
            "line_4": 450.00,
            "line_5": 0.00,
            "line_6": 2450.00
        },
        "section_2": {
            "line_41": 8000.00,
            "line_42": 1600.00,
            "line_43": 2000.00,
            "line_44": 180.00,
            "line_45": 1780.00
        },
        "section_4": {
            "line_70": 2450.00,
            "line_71": 1780.00,
            "line_72": 670.00
        }
    }
}
```

## Потребители и права

### Автентикация

#### Логване
```http
POST /v1/auth/login
```

**Тяло на заявката:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Отговор:**
```json
{
    "success": true,
    "data": {
        "access_token": "jwt_token_here",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
            "id": "uuid",
            "email": "user@example.com",
            "full_name": "Име Фамилия",
            "organizations": [
                {
                    "id": "uuid",
                    "name": "Организация ООД",
                    "slug": "org-ood",
                    "role": "administrator"
                }
            ]
        }
    }
}
```

#### Опресняване на токен
```http
POST /v1/auth/refresh
```

#### Изход
```http
POST /v1/auth/logout
```

### Потребители

#### Списък с потребители
```http
GET /v1/users
```

#### Нов потребител
```http
POST /v1/users
```

**Тяло на заявката:**
```json
{
    "email": "newuser@example.com",
    "full_name": "Нов Потребител",
    "password": "password123",
    "role_id": "uuid",
    "organization_id": "uuid"
}
```

## Webhooks

### Конфигуриране на webhooks

#### Списък с webhooks
```http
GET /v1/webhooks
```

#### Нов webhook
```http
POST /v1/webhooks
```

**Тяло на заявката:**
```json
{
    "url": "https://your-app.com/webhook",
    "events": ["invoice.created", "invoice.paid", "purchase_order.received"],
    "secret": "webhook_secret_here",
    "active": true
}
```

### Събития

#### Фактури
- `invoice.created` - Нова фактура
- `invoice.issued` - Издадена фактура
- `invoice.paid` - Платена фактура
- `invoice.cancelled` - Анулирана фактура

#### Поръчки
- `purchase_order.created` - Нова поръчка
- `purchase_order.confirmed` - Потвърдена поръчка
- `purchase_order.received` - Получена поръчка

#### Оферти
- `quotation.created` - Нова оферта
- `quotation.accepted` - Приета оферта
- `quotation.rejected` - Отхвърлена оферта

#### Склад
- `stock_movement.created` - Ново движение
- `stock_level.low` - Ниска наличност
- `product.out_of_stock` - Изчерпан продукт

### Webhook payload

#### Пример payload
```json
{
    "event": "invoice.created",
    "timestamp": "2025-01-14T10:30:00Z",
    "organization_id": "uuid",
    "data": {
        "id": "uuid",
        "invoice_no": "ИН0000000001",
        "status": "draft",
        "total_amount": 1200.00
    }
}
```

## Ограничения и квоти

### Rate limiting

#### Стандартни лимити
- 1000 заявки на час на IP адрес
- 10,000 заявки на час на потребител
- 100,000 заявки на час на организация

#### Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642147200
```

### Размер на данни

#### Request лимити
- Макс. размер на request: 10MB
- Макс. брой записи в batch: 100
- Макс. размер на файл: 50MB

#### Response лимити
- Макс. брой записи в page: 100
- Макс. размер на response: 50MB

## SDK и библиотеки

### Официални SDK-та

#### Python
```bash
pip install barasurya-python
```

```python
from barasurya import BarasuryaClient

client = BarasuryaClient(
    api_key="your_api_key",
    organization_id="uuid"
)

# Създаване на фактура
invoice = client.invoices.create({
    "customer_id": "uuid",
    "issue_date": "2025-01-14",
    "invoice_lines": [
        {
            "product_id": "uuid",
            "quantity": 10,
            "unit_price": 100.00
        }
    ]
})
```

#### JavaScript
```bash
npm install barasurya-js
```

```javascript
import { BarasuryaClient } from 'barasurya-js';

const client = new BarasuryaClient({
    apiKey: 'your_api_key',
    organizationId: 'uuid'
});

// Създаване на фактура
const invoice = await client.invoices.create({
    customerId: 'uuid',
    issueDate: '2025-01-14',
    invoiceLines: [
        {
            productId: 'uuid',
            quantity: 10,
            unitPrice: 100.00
        }
    ]
});
```

## Тестване

### Test environment
```
Base URL: https://api-test.barasurya.com/v1
```

### Test данни
- Тестови организации са предварително създадени
- Може да се създават тестови данни
- Всички операции са безплатни в test среда

### Примери

#### cURL примери
```bash
# Логване
curl -X POST https://api-test.barasurya.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Списък с фактури
curl -X GET https://api-test.barasurya.com/v1/invoices \
  -H "Authorization: Bearer jwt_token_here" \
  -H "X-Organization-ID: uuid"

# Нова фактура
curl -X POST https://api-test.barasurya.com/v1/invoices \
  -H "Authorization: Bearer jwt_token_here" \
  -H "X-Organization-ID: uuid" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "uuid",
    "issue_date": "2025-01-14",
    "invoice_lines": [
      {
        "product_id": "uuid",
        "quantity": 10,
        "unit_price": 100.00
      }
    ]
  }'
```

## Поддръжка

### Документация
- API документация: https://docs.barasurya.com/api
- Примери: https://github.com/barasurya/api-examples
- SDK-та: https://github.com/barasurya/sdks

### Контакт
- Email: api-support@barasurya.com
- Status page: https://status.barasurya.com
- Support: https://support.barasurya.com

### Changelog
- API промени: https://docs.barasurya.com/changelog
- Breaking changes: https://docs.barasurya.com/breaking-changes
- Roadmap: https://docs.barasurya.com/roadmap