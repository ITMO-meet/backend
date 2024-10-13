# ITMO-meet Backend
Это репозиторий бэкенда, который обрабатывает запросы с клиентской части

## Getting started
Для установки зависимостей:

`pip install -r requirements.txt`

## Testing
Для запуска тестов:

`pytest tests/unit` - запуск юнит тестов

`pytest tests/unit --cov=app --cov-fail-under=80` - запуск юнит тестов с покрытием

`pytest tests/integ` - запуск интеграционных тестов

`pytest tests/integ --cov=app --cov-fail-under=80` - запуск интеграционных тестов с покрытием
