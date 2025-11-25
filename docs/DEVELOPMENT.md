# Документация для разработчиков

## Развёртывание проекта

### Требования

- Docker и Docker Compose

### Развёртывание через Docker

1. **Клонировать репозиторий** (если необходимо):
```bash
git clone https://github.com/Vergelsky/crm-lead-router.git
cd crm-lead-router
```

2. **Запустить контейнеры**:
```bash
docker-compose up -d
```

Это запустит два контейнера:
- `leads_crm_db` - контейнер для хранения базы данных SQLite
- `leads_crm_app` - контейнер с приложением

3. **Применить миграции базы данных**:
```bash
docker-compose exec app alembic upgrade head
```

4. **Проверить работу приложения**:
```bash
curl http://localhost:8000/health
```

Приложение будет доступно по адресу `http://localhost:8000`
Документация API (Swagger): `http://localhost:8000/docs`
Альтернативная документация (ReDoc): `http://localhost:8000/redoc`

## Работа с миграциями Alembic

Все миграции создаются и применяются только в Docker контейнере.

1. **Создать новую миграцию** (автогенерация на основе изменений моделей):
```bash
docker-compose exec app alembic revision --autogenerate -m "описание изменений"
```

2. **Создать пустую миграцию** (для ручных изменений):
```bash
docker-compose exec app alembic revision -m "описание изменений"
```

3. **Применить миграции**:
```bash
docker-compose exec app alembic upgrade head
```

4. **Откатить последнюю миграцию**:
```bash
docker-compose exec app alembic downgrade -1
```

5. **Откатить все миграции**:
```bash
docker-compose exec app alembic downgrade base
```

6. **Просмотреть текущую версию**:
```bash
docker-compose exec app alembic current
```

7. **Просмотреть историю миграций**:
```bash
docker-compose exec app alembic history
```

### Структура миграций

Миграции хранятся в директории `alembic/versions/`. Каждая миграция содержит:
- `upgrade()` - применение изменений
- `downgrade()` - откат изменений

### Важные замечания

- **Всегда проверяйте автогенерированные миграции** перед применением
- **Тестируйте миграции** на тестовой базе данных перед продакшеном
- **Не редактируйте применённые миграции** - создавайте новые
- **Используйте транзакции** для критичных изменений

## Структура проекта

```
.
├── alembic/                 # Миграции Alembic
│   ├── versions/            # Файлы миграций
│   ├── env.py              # Конфигурация Alembic
│   └── script.py.mako      # Шаблон миграций
├── app/                     # Основной код приложения
│   ├── api/                # API слой (FastAPI роуты)
│   │   ├── operators.py    # Эндпоинты операторов
│   │   ├── sources.py      # Эндпоинты источников
│   │   ├── contacts.py     # Эндпоинты обращений
│   │   ├── leads.py        # Эндпоинты лидов
│   │   ├── schemas.py      # Pydantic схемы
│   │   └── main.py         # Главный FastAPI app
│   ├── domain/             # Доменный слой
│   │   └── models.py       # SQLAlchemy модели
│   ├── infrastructure/     # Инфраструктурный слой
│   │   └── repositories.py # Репозитории для работы с БД
│   ├── services/           # Сервисный слой (бизнес-логика)
│   │   └── distribution_service.py  # Логика распределения
│   ├── core/               # Ядро приложения
│   │   ├── config.py       # Настройки
│   │   └── database.py     # Подключение к БД
│   └── main.py             # Точка входа
├── docs/                   # Документация
│   └── DEVELOPMENT.md      # Этот файл
├── alembic.ini             # Конфигурация Alembic
├── docker-compose.yml      # Docker Compose конфигурация (app + db)
├── Dockerfile              # Docker образ для приложения
├── requirements.txt        # Python зависимости
└── README.md               # Основная документация

**Примечание:** База данных SQLite хранится в Docker volume `db_data` и доступна через контейнер `db`.
```

## Архитектурные принципы

### Hexagonal Architecture (Ports & Adapters)

Приложение разделено на слои:

1. **Domain Layer** (`app/domain/`) - доменные модели и бизнес-логика
2. **Infrastructure Layer** (`app/infrastructure/`) - реализация репозиториев, работа с БД
3. **API Layer** (`app/api/`) - HTTP интерфейс, FastAPI роуты
4. **Service Layer** (`app/services/`) - сервисы с бизнес-логикой

### Dependency Injection

Зависимости инжектируются через FastAPI Depends:
```python
async def get_operator(db: AsyncSession = Depends(get_db)):
    # ...
```

### Repository Pattern

Доступ к данным осуществляется через репозитории, что позволяет:
- Изолировать бизнес-логику от деталей БД
- Легко тестировать (можно мокировать репозитории)
- Легко менять реализацию (например, с SQLite на PostgreSQL)

## Разработка

### Добавление нового эндпоинта

1. Создать схему в `app/api/schemas.py`
2. Добавить роутер в `app/api/`
3. Зарегистрировать роутер в `app/api/main.py`

### Добавление новой модели

1. Создать модель в `app/domain/models.py`
2. Создать миграцию в контейнере: `docker-compose exec app alembic revision --autogenerate -m "add new model"`
3. Применить миграцию: `docker-compose exec app alembic upgrade head`

### Тестирование

Интеграционные тесты проверяют работоспособность всех API эндпоинтов.

**Запуск всех тестов:**
```bash
docker-compose exec app pytest
```

**Запуск с подробным выводом:**
```bash
docker-compose exec app pytest -v
```

**Запуск конкретного тестового файла:**
```bash
docker-compose exec app pytest tests/test_operators.py
```

**Запуск конкретного теста:**
```bash
docker-compose exec app pytest tests/test_operators.py::test_create_operator
```

**Структура тестов:**
- `tests/conftest.py` - фикстуры для тестов (тестовая БД, клиент)
- `tests/test_operators.py` - тесты CRUD операций для операторов
- `tests/test_sources.py` - тесты для источников и настройки распределения
- `tests/test_contacts.py` - тесты регистрации обращений и автоматического распределения
- `tests/test_leads.py` - тесты работы с лидами и дедупликации

Все тесты используют in-memory SQLite базу данных, которая создаётся и удаляется для каждого теста, что обеспечивает изоляцию тестов.

### Логирование

Логи приложения выводятся в консоль. В продакшене рекомендуется настроить централизованное логирование.

## Переменные окружения

Переменные окружения задаются в `docker-compose.yml` или через файл `.env` (который будет загружен автоматически).

Для настройки создайте файл `.env` на основе примера:

```bash
cp env.example .env
```

Затем при необходимости отредактируйте значения в файле `.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./data/leads_crm.db
API_V1_PREFIX=/api/v1
PROJECT_NAME=Leads CRM
PROJECT_VERSION=1.0.0
```

**Важно:** Файл `.env` находится в `.gitignore` и не попадает в репозиторий. Используйте `env.example` как шаблон.

## Отладка

### Просмотр логов контейнера

```bash
docker-compose logs -f app
```

### Вход в контейнер

```bash
docker-compose exec app bash
```

### Проверка базы данных

```bash
# Войти в контейнер
docker-compose exec app bash

# Использовать sqlite3 для просмотра БД
sqlite3 /app/data/leads_crm.db
.tables
SELECT * FROM operators;
```

## Производительность

### Оптимизация запросов

- Используются индексы на часто запрашиваемых полях
- Используется `selectinload` для eager loading связей
- Асинхронные запросы для неблокирующей работы

### Масштабирование

Для продакшена рекомендуется:
- Заменить SQLite на PostgreSQL
- Добавить Redis для кеширования
- Настроить connection pooling
- Добавить мониторинг и логирование

## Безопасность

- Валидация входных данных через Pydantic
- Обработка ошибок с понятными сообщениями
- SQL injection защита через SQLAlchemy ORM

Для продакшена рекомендуется добавить:
- Аутентификацию и авторизацию
- Rate limiting
- HTTPS
- CORS настройки для конкретных доменов

## Полезные команды

### Остановка контейнеров
```bash
docker-compose down
```

### Пересборка образов
```bash
docker-compose build --no-cache
```

### Очистка данных
```bash
docker-compose down -v  # Удаляет volumes (включая базу данных)
```

**Внимание:** Команда `docker-compose down -v` удалит все данные базы данных, так как они хранятся в named volume `db_data`.

### Просмотр использования ресурсов
```bash
docker-compose stats
```

### Работа с контейнером базы данных
```bash
# Просмотр логов контейнера БД
docker-compose logs db

# Вход в контейнер БД
docker-compose exec db sh


## Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs app`
2. Проверьте статус контейнеров: `docker-compose ps`
3. Убедитесь, что миграции применены: `docker-compose exec app alembic current`
4. Проверьте доступность порта 8000

