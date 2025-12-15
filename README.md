# Barasurya ERP - Българска ERP система

<div align="center">
  <p>
    <img width="100%" src="./img/barasurya-wide.png" alt="Barasurya banner">
  </p>

  <p>
    <strong>Модерна ERP система за българския бизнес</strong>
  </p>

  <p>
    <a href="#бърз-старт">Бърз старт</a> •
    <a href="#функционалности">Функционалности</a> •
    <a href="#технологии">Технологии</a> •
    <a href="#документация">Документация</a>
  </p>
</div>

---

## Бърз старт

### 1. Клониране на репозиторията

```bash
git clone https://github.com/barasurya/barasurya.git
cd barasurya
```

### 2. Конфигурация

```bash
# Копирайте примерния .env файл
cp .env.example .env

# Редактирайте .env с вашите настройки
nano .env
```

**Важни настройки в `.env`:**
```env
# Сменете тези стойности!
SECRET_KEY=your-super-secret-key-here
FIRST_SUPERUSER=admin@yourcompany.bg
FIRST_SUPERUSER_PASSWORD=YourSecurePassword123!
POSTGRES_PASSWORD=YourDatabasePassword!
```

### 3. Стартиране с Docker

```bash
# Стартиране на всички контейнери
docker compose up -d

# Изчакайте базата да стартира, след това стартирайте prestart
docker compose run --rm prestart
```

### 4. Достъп до приложението

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Adminer (DB):** http://localhost:8080
- **Mailcatcher:** http://localhost:1080

---

## Функционалности

### Основни модули

| Модул | Описание |
|-------|----------|
| **Организации** | Multi-tenant архитектура с роли (Admin, Manager, Member) |
| **Контрагенти** | Клиенти и доставчици с VIES валидация на ДДС номера |
| **Фактури** | Продажби и покупки с автоматично осчетоводяване |
| **ДДС** | Дневници за покупки/продажби, ДДС декларации |
| **Счетоводство** | Сметкоплан, дневникови записи, оборотни ведомости |
| **Банки** | Банкови сметки, транзакции, импорт на извлечения |
| **Склад** | Продукти, складове, наличности |
| **ДМА** | Дълготрайни материални активи с амортизации |
| **Рецепти** | Производствени рецепти за калкулация |

### AI функционалности

| Функция | Описание |
|---------|----------|
| **AI Фактури** | Автоматично разпознаване на фактури с Azure Document Intelligence |
| **OCR обработка** | Извличане на данни от PDF документи |

### Настройки на организацията

| Настройка | Описание |
|-----------|----------|
| **SMTP** | Конфигурация на email сървър |
| **Azure AI** | API ключове за Document Intelligence |
| **Сметки по подразбиране** | Клиенти, Доставчици, ДДС, Приходи, Каса, Банка |

---

## Технологии

### Backend
- **FastAPI** - Модерен Python web framework
- **SQLModel** - ORM базиран на SQLAlchemy и Pydantic
- **PostgreSQL** - Релационна база данни
- **Alembic** - Миграции на базата данни
- **JWT** - Автентикация с токени

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool
- **Chakra UI** - Компонентна библиотека
- **TanStack Query** - Data fetching
- **React Hook Form** - Форми
- **i18next** - Интернационализация (BG/EN)

### DevOps
- **Docker & Docker Compose** - Контейнеризация
- **Traefik** - Reverse proxy с автоматични HTTPS сертификати
- **GitHub Actions** - CI/CD

---

## Структура на проекта

```
barasurya/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── crud/           # Database operations
│   │   ├── models/         # SQLModel модели
│   │   ├── alembic/        # Миграции
│   │   └── services/       # Бизнес логика
│   └── scripts/            # Помощни скриптове
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React компоненти
│   │   ├── routes/         # Страници
│   │   ├── client/         # Auto-generated API client
│   │   └── i18n/           # Преводи
│   └── public/             # Статични файлове
├── docs/                   # Документация
├── docker-compose.yml      # Production setup
├── docker-compose.override.yml  # Development setup
└── .env.example            # Примерна конфигурация
```

---

## Документация

- [Разработка](./development.md) - Настройка на development среда
- [Backend](./backend/README.md) - Backend документация
- [Frontend](./frontend/README.md) - Frontend документация
- [Deployment](./deployment.md) - Инструкции за deploy
- [Multi-tenant архитектура](./docs/multi-tenant-architecture.md)
- [ДДС модул](./docs/VAT_MODULE_BG.md) - Българско ДДС
- [Текущо състояние](./docs/CURRENT_STATE_BG.md) - Какво е реализирано

---

## Принос към проекта

Приветстваме приноса към проекта!

1. Fork-нете репозиторията
2. Създайте feature branch (`git checkout -b feature/nova-funkcionalnost`)
3. Commit-нете промените (`git commit -m 'Добавяне на нова функционалност'`)
4. Push-нете към branch-а (`git push origin feature/nova-funkcionalnost`)
5. Отворете Pull Request

---

## Оригинален шаблон

Базиран на [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template).

---

## Лиценз

MIT License - свободни сте да използвате, модифицирате и разпространявате.

---

## Автори

**Създадено от:** Димитър Гигов / Dimitar Gigov

**Repository:** [https://github.com/barasurya/barasurya](https://github.com/barasurya/barasurya)

**Website:** [https://cyberbuch.org/](https://cyberbuch.org/)

---

<div align="center">
  <p>
    <sub>Направено с ❤️ за българския бизнес</sub>
  </p>
</div>
