# Changelog

## [1.0.0] - 2024-12-15

### Първо официално издание

#### Актуализация на документацията
- **README.md** - Обновен с новия URL на репозиторията (barasurya/barasurya)
- **API_DOCUMENTATION_BG.md** - Коригиран URL за development средата
- **docs/README.md** - Актуализирана дата на последно обновяване

#### Проектни промени
- **Бекенд версия: 1.0.0** (barasurya-erp)
- **Фронтенд версия: 1.0.0** (barasurya-erp-frontend)
- **Технологичен стек** - Python 3.12+, FastAPI 0.115.6+, React 18.3.1+, TypeScript 5.7.2+

---

## [0.3.0] - 2024-12-14

### Добавено

#### Bank модул (нов)
Пълна имплементация на банков модул за управление на банкови сметки, транзакции и импорт.

**Модели:**
- `BankAccount` - Банкови сметки с поддръжка на IBAN, BIC, различни типове сметки
- `BankTransaction` - Банкови транзакции с връзка към счетоводни записи
- `BankStatement` - Банкови извлечения
- `BankImport` - Импорт на банкови данни (Salt Edge, файлов импорт)
- `BankProfile` - Конфигурация за банкови профили с поддръжка на MT940, CAMT053

**API endpoints:**
- `GET/POST /api/bank-accounts` - CRUD за банкови сметки
- `GET/PUT/DELETE /api/bank-accounts/{id}` - Операции по ID
- `GET/POST /api/bank-transactions` - CRUD за транзакции
- `POST /api/bank-transactions/{id}/process` - Обработка на транзакция

**Миграция:** `e5f6a7b8c9d0_create_bank_tables.py`

#### VAT модул (нов)
Имплементация на ДДС отчетност съгласно българското законодателство (ЗДДС).

**Модели:**
- `VatReturn` - ДДС декларации (месечни/тримесечни)
- `VatSalesRegister` - Дневник продажби с всички операционни кодове
- `VatPurchaseRegister` - Дневник покупки с данъчен кредит

**Функционалности:**
- Автоматично определяне на VAT operation codes (2-11, 2-17, и др.)
- VIES индикатори (к3, к4, к5)
- Обратно начисляване (reverse charge)
- Триъгълни операции
- Изчисление на ДДС за внасяне/възстановяване

**Миграция:** `f6a7b8c9d0e1_create_vat_tables.py`

#### SAF-T модул (подобрен)
- Добавени SAF-T номенклатурни таблици
- Генератори за Header, MasterFiles, GeneralLedgerEntries, SourceDocuments
- API endpoint за генериране на SAF-T файлове

**SAF-T номенклатури:**
- `AssetMovementType` - Типове движения на активи
- `Country` - Държави
- `IbanFormat` - Формати на IBAN
- `InventoryType` - Типове инвентар
- `InvoiceType` - Типове фактури
- `NC8Taric` - КН кодове
- `PaymentMethod` - Методи на плащане
- `StockMovementType` - Типове складови движения
- `VatTaxType` - Типове ДДС

#### Счетоводен модул (подобрен)
- `JournalEntry` - Счетоводни записи
- `EntryLine` - Редове на записи
- `Asset` - Дълготрайни активи
- `AssetDepreciationSchedule` - Амортизационен план
- `AssetTransaction` - Транзакции по активи

### Променено
- Разширен `Organization` модел с връзки към Bank, VAT, Journal модули
- Добавени счетоводни конфигурации в Organization (accounts_receivable, sales_revenue, vat_payable, etc.)
- Актуализиран `Invoice` модел с връзка към VatSalesRegister
- Добавен EIK поле в Organization за SAF-T съвместимост

### Поправено
- Import error в `saft_service.py` - липсващ `Optional` тип

### Миграции
```
29b8c3a1e8c7 - Add SAFT nomenclature tables
3a3d9f3e3d3b - Add SAFT fields to Customer and Supplier
4e5f3f4e4e4e - Add asset transactions and SAFT fields to assets
5f0f3f5f5f5f - Create SAFT NC8/TARIC codes table
6a1b1a1b1a1b - Add year to SAFT NC8/TARIC codes
7b2c2b2c2b2c - Add SAFT fields to Organization
8c3d3d3d3d3d - Add EIK to Organization
9d4d4d4d4d4d - Create journal_entry and entry_line tables
a1b2c3d4e5f6 - Add accounting config to Organization
b2c3d4e5f6a7 - Add purchase accounting config to Organization
c3d4e5f6a7b8 - Add cash account config to Organization
d4e5f6a7b8c9 - Create asset tables
e5f6a7b8c9d0 - Create bank tables
f6a7b8c9d0e1 - Create VAT tables
```

---

## [0.2.0] - 2024-12-13

### Добавено
- Multi-tenant архитектура с organization-based изолация на данни
- RBAC система с roles и permissions
- Базови CRUD операции за customers, suppliers, items, purchases, sales

---

## [0.1.0] - Начална версия

### Добавено
- Първоначална структура на проекта
- FastAPI backend
- React frontend с Chakra UI
- PostgreSQL база данни
- JWT authentication
