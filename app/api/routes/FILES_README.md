# 📁 File Management System

Полнофункциональная система управления файлами через MinIO.

## ✨ Возможности

- ✅ **Загрузка файлов** - поддержка любых расширений файлов
- ✅ **Скачивание файлов** - загрузка файлов с сервера
- ✅ **Просмотр информации** - получение метаданных о файле по ID
- ✅ **Список файлов** - просмотр всех загруженных файлов
- ✅ **Мои файлы** - просмотр только своих загруженных файлов
- ✅ **Удаление файлов** - удаление файлов (только автор или админ)
- ✅ **Мягкое удаление** - файлы помечаются как удаленные, но не удаляются из MinIO

## 🔧 API Endpoints

### Загрузка файла
```
POST /files/upload
```
**Параметры:**
- `file` (multipart/form-data) - файл для загрузки

**Ответ:**
```json
{
  "id": "uuid",
  "file_name": "example.pdf",
  "minio_url": "http://minio:9000/bucket/uuid_example.pdf",
  "file_size": 12345,
  "created_at": "2026-06-14T10:00:00"
}
```

### Получить информацию о файле
```
GET /files/{file_id}
```

### Скачать файл
```
GET /files/{file_id}/download
```
Возвращает файл как attachment для скачивания.

### Удалить файл
```
DELETE /files/{file_id}
```
Возвращает статус 204 No Content при успешном удалении.

### Список всех файлов
```
GET /files/
```
**Параметры:**
- `skip` (int, default=0) - количество записей для пропуска
- `limit` (int, default=100) - максимальное количество записей

### Список моих файлов
```
GET /files/my/files
```
**Параметры:**
- `skip` (int, default=0) - количество записей для пропуска
- `limit` (int, default=100) - максимальное количество записей

## 🗄️ Структура базы данных

### Таблица `files`
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    minio_object_name VARCHAR(500) NOT NULL UNIQUE,
    file_size INTEGER NOT NULL,
    content_type VARCHAR(255) NOT NULL,
    minio_url VARCHAR(1000) NOT NULL,
    uploaded_by UUID NOT NULL FOREIGN KEY REFERENCES users(id),
    created_at DATETIME NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

## 🚀 Использование

### Python пример (requests)
```python
import requests

# Загрузка файла
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/files/upload',
        files=files,
        headers={'Authorization': 'Bearer YOUR_TOKEN'}
    )
    print(response.json())

# Скачивание файла
response = requests.get(
    'http://localhost:8000/files/{file_id}/download',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
with open('downloaded_file.pdf', 'wb') as f:
    f.write(response.content)

# Получение информации о файле
response = requests.get(
    'http://localhost:8000/files/{file_id}',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
print(response.json())

# Список всех файлов
response = requests.get(
    'http://localhost:8000/files/',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
print(response.json())

# Список моих файлов
response = requests.get(
    'http://localhost:8000/files/my/files',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
print(response.json())

# Удаление файла
response = requests.delete(
    'http://localhost:8000/files/{file_id}',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
```

### Bash пример (curl)
```bash
# Загрузка файла
curl -X POST http://localhost:8000/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"

# Скачивание файла
curl -X GET http://localhost:8000/files/{file_id}/download \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o downloaded_file.pdf

# Получение информации
curl -X GET http://localhost:8000/files/{file_id} \
  -H "Authorization: Bearer YOUR_TOKEN"

# Список файлов
curl -X GET http://localhost:8000/files/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Удаление файла
curl -X DELETE http://localhost:8000/files/{file_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔐 Безопасность

- ✅ Все endpoints требуют аутентификации
- ✅ Пользователи могут удалять только свои файлы (администратор может удалять любые)
- ✅ Файлы доступны через защищенные endpoints
- ✅ Поддержка различных типов контента (MIME types)

## 📊 Модели данных

### File Model
```python
id: UUID                  # Уникальный идентификатор
file_name: str           # Имя файла
minio_object_name: str   # Имя объекта в MinIO
file_size: int           # Размер в байтах
content_type: str        # MIME type
minio_url: str          # URL доступа
uploaded_by: UUID        # ID пользователя
created_at: datetime     # Дата загрузки
is_deleted: bool         # Флаг удаления
```

## 🐳 Docker Compose

MinIO уже сконфигурирован в docker-compose:
- **Endpoint**: `minio:9000`
- **Console**: `http://localhost:9001`
- **Bucket**: `app-files` (или согласно `.env`)

Для доступа к консоли MinIO используйте credentials из `.env`:
- Username: `MINIO_ACCESS_KEY`
- Password: `MINIO_SECRET_KEY`

## 🔄 Миграция БД

Миграция для создания таблицы `files`:
```bash
docker compose exec backend alembic upgrade head
```

## 📝 Примечания

- Файлы хранятся в MinIO, метаданные - в PostgreSQL
- Мягкое удаление: файлы помечаются как удаленные, но физически остаются в MinIO
- Размер файла автоматически сохраняется при загрузке
- Поддерживается пагинация для списков файлов
