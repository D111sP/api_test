# Рассылка API

API для управления рассылками.

## Запуск проекта

1. Установите Python версии 3.9, если у вас его еще нет.
2. Установите зависимости, выполнив команду `pip install -r requirements.txt`.
3. Запустите приложение, выполнив команду `python app.py`.
4. После успешного запуска, сервис будет доступен по адресу `http://localhost:5000`.

## API

- Создание нового клиента: `POST /clients`
- Обновление данных атрибутов клиента: `PUT /clients/{client_id}`
- Удаление клиента: `DELETE /clients/{client_id}`
- Создание новой рассылки: `POST /deliveries`
- Получение общей статистики рассылок: `GET /statistics`
- Получение детальной статистики рассылки: `GET /deliveries/{delivery_id}/statistics`

Подробная документация API доступна в файле openapi.json.

## Требования

- Python 3.9
- Flask 2.0.1
- Flask-SQLAlchemy 3.0.1
- requests 2.26.0