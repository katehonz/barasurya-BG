# Инсталация и настройка

## Преглед

Този документ описва процеса на инсталация и настройка на Barasurya ERP система, включително изисквания, стъпки за инсталация, конфигурация и първоначално настройване.

## Системни изисквания

### Минимални изисквания

#### Хардуер
- **CPU**: 2 ядра (64-bit)
- **RAM**: 4GB RAM
- **Диск**: 20GB свободно пространство
- **Мрежа**: Интернет връзка

#### Софтуер
- **Операционна система**: Linux (Ubuntu 20.04+, CentOS 8+), macOS 10.15+, Windows 10+
- **Python**: 3.9+
- **Node.js**: 16+
- **PostgreSQL**: 13+
- **Redis**: 6+

### Препоръчителни изисквания

#### Хардуер
- **CPU**: 4+ ядра (64-bit)
- **RAM**: 8GB+ RAM
- **Диск**: 50GB+ SSD
- **Мрежа**: Стабилна интернет връзка

#### Софтуер
- **Операционна система**: Ubuntu 22.04 LTS
- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 15+
- **Redis**: 7+

## Инсталация

### 1. Клониране на репозиторито

```bash
# Клониране на проекта
git clone https://github.com/barasurya/barasurya.git
cd barasurya

# Проверка на версиите
git tag -l
git checkout v1.0.0  # последна стабилна версия
```

### 2. Backend инсталация

```bash
# Влизане в backend директорията
cd backend

# Създаване на виртуална среда
python3 -m venv venv

# Активиране на виртуалната среда
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Инсталация на зависимости
pip install -r requirements.txt

# Инсталация на development зависимости
pip install -r requirements-dev.txt
```

### 3. Frontend инсталация

```bash
# Влизане в frontend директорията
cd ../frontend

# Инсталация на зависимости
npm install

# Инсталация на development зависимости
npm install --dev
```

### 4. Database настройка

#### PostgreSQL инсталация

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS (Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
- Изтеглете PostgreSQL от https://www.postgresql.org/download/windows/
- Инсталирайте с GUI инсталатора

#### Създаване на база данни

```bash
# Влизане в PostgreSQL
sudo -u postgres psql

# Създаване на потребител
CREATE USER barasurya WITH PASSWORD 'your_password';

# Създаване на база данни
CREATE DATABASE barasurya OWNER barasurya;

# Достъп на потребителя
GRANT ALL PRIVILEGES ON DATABASE barasurya TO barasurya;

# Изход от PostgreSQL
\q
```

### 5. Redis инсталация

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Windows:**
- Изтеглете Redis от https://github.com/microsoftarchive/redis/releases
- Стартирайте redis-server.exe

## Конфигурация

### 1. Environment променливи

#### Backend конфигурация

Създайте `.env` файл в `backend/` директорията:

```bash
# Database конфигурация
DATABASE_URL=postgresql://barasurya:your_password@localhost:5432/barasurya

# Redis конфигурация
REDIS_URL=redis://localhost:6379/0

# JWT конфигурация
SECRET_KEY=your_super_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email конфигурация
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAILS_FROM_EMAIL=noreply@yourcompany.com
EMAILS_FROM_NAME=Barasurya ERP

# Application конфигурация
ENVIRONMENT=development
DEBUG=true
API_V1_STR=/api/v1
PROJECT_NAME=Barasurya ERP

# CORS конфигурация
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# File upload конфигурация
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# Logging конфигурация
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

#### Frontend конфигурация

Създайте `.env` файл в `frontend/` директорията:

```bash
# API конфигурация
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# Application конфигурация
VITE_APP_NAME=Barasurya ERP
VITE_APP_VERSION=1.0.0

# Feature flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=true
```

### 2. Database миграции

```bash
# Влизане в backend директорията
cd backend

# Активиране на виртуалната среда
source venv/bin/activate

# Генериране на миграции (ако е необходимо)
alembic revision --autogenerate -m "Initial migration"

# Изпълнение на миграциите
alembic upgrade head

# Проверка на статуса
alembic current
```

### 3. Първоначални данни

```bash
# Създаване на първоначални данни
python scripts/initial_data.py

# Създаване на супер потребител
python scripts/create_superuser.py
```

## Стартиране на приложението

### 1. Development режим

#### Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run dev
```

### 2. Production режим

#### Backend с Gunicorn
```bash
cd backend
source venv/bin/activate
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend build
```bash
cd frontend
npm run build
npm run preview
```

### 3. Docker инсталация

#### Docker Compose
```bash
# Стартиране на всички услуги
docker-compose up -d

# Проверка на статус
docker-compose ps

# Логове
docker-compose logs -f

# Спиране
docker-compose down
```

#### Dockerfile за backend
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### Dockerfile за frontend
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## Първоначално настройване

### 1. Достъп до системата

- **Frontend**: http://localhost:5173 (development) или http://localhost:3000 (production)
- **Backend API**: http://localhost:8000/api/v1
- **API документация**: http://localhost:8000/docs

### 2. Създаване на организация

1. Влезте със супер потребител акаунт
2. Отидете в "Настройки" → "Организации"
3. Натиснете "Нова организация"
4. Попълнете данните:
   - Име на организацията
   - ЕИК/БУЛСТАТ
   - Адрес
   - Данъчни настройки
   - Валутни настройки

### 3. Настройка на потребители

1. Отидете в "Настройки" → "Потребители"
2. Натиснете "Нов потребител"
3. Попълнете данните:
   - Имейл
   - Име
   - Роля
   - Права

### 4. Настройка на справочници

#### Клиенти
```bash
# Импорт на клиенти от CSV
python scripts/import_customers.py --file customers.csv

# Ръчно създаване през API
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Клиент ООД",
    "eik": "123456789",
    "address": "гр. София, ул. Васил Левски 1",
    "email": "client@example.com",
    "phone": "02 123 456"
  }'
```

#### Доставчици
```bash
# Импорт на доставчици от CSV
python scripts/import_suppliers.py --file suppliers.csv
```

#### Продукти
```bash
# Импорт на продукти от CSV
python scripts/import_products.py --file products.csv
```

#### Складове
```bash
# Създаване на основен склад
curl -X POST http://localhost:8000/api/v1/warehouses \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "MAIN",
    "name": "Основен склад",
    "address": "гр. София, ул. Индустриална 1",
    "costing_method": "weighted_average"
  }'
```

### 5. Настройка на счетоводен план

```bash
# Импорт на стандартен счетоводен план
python scripts/import_chart_of_accounts.py --file accounts.csv

# Ръчно създаване на сметки
curl -X POST http://localhost:8000/api/v1/accounts \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "301",
    "name": "Суровини и материали",
    "type": "asset",
    "parent_id": null
  }'
```

## SSL и HTTPS настройка

### 1. Self-signed сертификат (development)

```bash
# Генериране на сертификат
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Конфигуриране на nginx
server {
    listen 443 ssl;
    server_name localhost;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Let's Encrypt (production)

```bash
# Инсталация на Certbot
sudo apt install certbot python3-certbot-nginx

# Генериране на сертификат
sudo certbot --nginx -d yourdomain.com

# Автоматично подновяване
sudo crontab -e
# Добавете: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Backup и recovery

### 1. Database backup

```bash
# Ръчен backup
pg_dump -h localhost -U barasurya barasurya > backup_$(date +%Y%m%d_%H%M%S).sql

# Автоматичен backup (cron)
0 2 * * * pg_dump -h localhost -U barasurya barasurya > /backups/daily/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

### 2. File backup

```bash
# Backup на файлове
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/

# Backup на конфигурация
tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz .env nginx.conf
```

### 3. Recovery

```bash
# Възстановяване на база данни
psql -h localhost -U barasurya barasurya < backup_20250114_020000.sql

# Възстановяване на файлове
tar -xzf uploads_backup_20250114_020000.tar.gz
```

## Мониторинг и логване

### 1. Application logging

```python
# Конфигурация на логване в backend/app/core/config.py
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default", "file"],
    },
}
```

### 2. System мониторинг

#### Prometheus + Grafana
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

#### Health checks
```bash
# Health check endpoint
curl http://localhost:8000/health

# Database health check
curl http://localhost:8000/health/db

# Redis health check
curl http://localhost:8000/health/redis
```

## Сигурност

### 1. Firewall конфигурация

```bash
# UFW конфигурация (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Блокиране на direct API достъп
```

### 2. Security headers

```nginx
# Добавяне в nginx.conf
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

### 3. Rate limiting

```python
# Конфигурация в backend/app/core/security.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour", "100/minute"]
)
```

## Производителност

### 1. Database оптимизация

```sql
-- Създаване на индекси
CREATE INDEX CONCURRENTLY idx_invoices_org_date ON invoices(organization_id, date_created);
CREATE INDEX CONCURRENTLY idx_customers_org_name ON customers(organization_id, name);
CREATE INDEX CONCURRENTLY idx_products_org_sku ON products(organization_id, sku);

-- Vacuum и analyze
VACUUM ANALYZE;
```

### 2. Caching

```python
# Redis кеширане
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Кеширане на данни
def get_products_cached(org_id):
    cache_key = f"products:{org_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    products = get_products_from_db(org_id)
    redis_client.setex(cache_key, 3600, json.dumps(products))
    return products
```

### 3. Load balancing

```nginx
# Nginx load balancer
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Трабълшутинг

### Общи проблеми

#### 1. Database connection errors
```bash
# Проверка на PostgreSQL статус
sudo systemctl status postgresql

# Проверка на connection
psql -h localhost -U barasurya -d barasurya

# Проверка на pg_hba.conf
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

#### 2. Redis connection errors
```bash
# Проверка на Redis статус
sudo systemctl status redis-server

# Тест на connection
redis-cli ping
```

#### 3. Permission errors
```bash
# Проверка на права
ls -la /path/to/uploads

# Коригиране на права
sudo chown -R www-data:www-data /path/to/uploads
sudo chmod -R 755 /path/to/uploads
```

#### 4. SSL/TLS errors
```bash
# Проверка на сертификат
openssl x509 -in /path/to/cert.pem -text -noout

# Тест на SSL connection
openssl s_client -connect yourdomain.com:443
```

### Логове и дебъгване

#### Application логове
```bash
# Real-time логове
tail -f backend/logs/app.log

# Грешки
grep ERROR backend/logs/app.log

# Database заявки
grep "SQL" backend/logs/app.log
```

#### System логове
```bash
# Nginx логове
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# PostgreSQL логове
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# System логове
sudo journalctl -u barasurya -f
```

## Поддръжка

### Документация
- API документация: http://localhost:8000/docs
- Потребителска документация: https://docs.barasurya.com
- GitHub repository: https://github.com/barasurya/barasurya

### Поддръжка
- Email: support@barasurya.com
- GitHub Issues: https://github.com/barasurya/barasurya/issues
- Discord: https://discord.gg/barasurya

### Ъпдейти
```bash
# Проверка за ъпдейти
git fetch origin
git log HEAD..origin/main --oneline

# Ъпгрейд
git pull origin main
pip install -r requirements.txt
alembic upgrade head
```

## Често задавани въпроси

### Q: Как да променя порта на приложението?
A: Променете `--port` параметъра при стартиране или променете `PORT` environment променлива.

### Q: Как да добавя нов потребител?
A: Използвайте API ендпойнта `/api/v1/users` или потребителския интерфейс.

### Q: Как да направя backup на данните?
A: Използвайте `pg_dump` за базата данни и `tar` за файловете.

### Q: Как да конфигурирам SSL?
A: Използвайте Let's Encrypt за production или self-signed сертификати за development.

### Q: Как да оптимизирам производителността?
A: Оптимизирайте базата данни, използвайте кеширане и load balancing.