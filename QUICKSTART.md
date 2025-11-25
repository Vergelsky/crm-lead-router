# Быстрый старт

## Запуск через Docker Compose

```bash
# 1. Запустить контейнеры (приложение и база данных)
docker-compose up -d

# 2. Применить миграции базы данных
docker-compose exec app alembic upgrade head

# 3. Проверить работу
curl http://localhost:8000/health
```

**Примечание:** База данных SQLite разворачивается в отдельном контейнере `db` с использованием Docker volume для хранения данных.

Приложение будет доступно по адресу: **http://localhost:8000**
Документация API: **http://localhost:8000/docs**

## Остановка

```bash
docker-compose down
```

## Полезные команды

```bash
# Просмотр логов приложения
docker-compose logs -f app

# Просмотр логов базы данных
docker-compose logs -f db

# Вход в контейнер приложения
docker-compose exec app bash

# Вход в контейнер базы данных
docker-compose exec db sh

# Создание новой миграции
docker-compose exec app alembic revision --autogenerate -m "описание"

# Применение миграций
docker-compose exec app alembic upgrade head

# Просмотр статуса всех контейнеров
docker-compose ps

# Запуск тестов
docker-compose exec app pytest
```

Подробная документация: [README.md](README.md) и [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

