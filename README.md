# Barasurya ERP - Българска версия

<div align="center">
  <p>
    <img width="100%" src="./img/barasurya-wide.png" alt="Barasurya banner">
  </p>
</div>

---

## Оригинален шаблон / Original Template

Първоначалният шаблон е базиран на [Full Stack FastAPI Template](https://github.com/fn-hide/barasurya) от fn-hide.

The original template is based on [Full Stack FastAPI Template](https://github.com/fn-hide/barasurya) by fn-hide.

**The Full Stack FastAPI Template is licensed under the terms of the MIT license.**

---

## Българска адаптация / Bulgarian Adaptation

Тази версия е адаптирана за **българското законодателство и счетоводна практика**.

Всеки може свободно да продължи по-нататъшната разработка.

This version is adapted for **Bulgarian legislation and accounting practices**.

Everyone is free to continue further development.

---

**Създадено от / Created by:** Димитър Гигов / Dimitar Gigov

**Website:** [https://cyberbuch.org/](https://cyberbuch.org/)

---

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
    - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
    - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
    - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🚀 [React](https://react.dev) for the frontend.
    - 💃 Using TypeScript, hooks, Vite, and other parts of a modern frontend stack.
    - 🎨 [Chakra UI](https://chakra-ui.com) for the frontend components.
    - 🤖 An automatically generated frontend client.
    - 🧪 [Playwright](https://playwright.dev) for End-to-End testing.
    - 🦇 Dark mode support.
- 🏢 **Multi-tenant architecture** with organization-based data isolation.
    - Users can belong to multiple organizations
    - Role-based access control (Admin, Manager, Member)
    - Easy organization switching
- 🌐 **Internationalization (i18n)** with Bulgarian and English support.
- 🏦 **Bank Module** - Full banking integration
    - Bank accounts management (IBAN, BIC, multiple currencies)
    - Bank transactions with journal entry integration
    - Bank statements and imports (MT940, CAMT053, Salt Edge)
- 📋 **VAT Module** - Bulgarian VAT compliance (ЗДДС)
    - VAT Returns (monthly/quarterly declarations)
    - Sales Register (Дневник продажби)
    - Purchase Register (Дневник покупки)
    - VIES indicators and reverse charge support
- 📊 **SAF-T Module** - Standard Audit File for Tax
    - SAF-T BG schema compliance
    - Header, MasterFiles, GeneralLedgerEntries, SourceDocuments
    - XML generation for NAP reporting
- 💼 **Accounting Module**
    - Journal entries with debit/credit lines
    - Fixed assets with depreciation schedules
    - Chart of accounts integration
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- ✅ Tests with [Pytest](https://pytest.org).
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Traefik proxy to handle automatic HTTPS certificates.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

## Documentations

- General Development: [development.md](./development.md).
- Backend: [backend/README.md](./backend/README.md).
- Frontend: [frontend/README.md](./frontend/README.md).
- Deployment: [deployment.md](./deployment.md).
- Multi-tenant Architecture: [docs/multi-tenant-architecture.md](./docs/multi-tenant-architecture.md).

## Release Notes

Check the file [release-notes.md](./release-notes.md).

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for detailed version history.

## License / Лиценз

This project is licensed under the terms of the **MIT license**.

Този проект е лицензиран под условията на **MIT лиценза**.
