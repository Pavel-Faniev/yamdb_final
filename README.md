### __Краткое описание проекта YaMDb__
***
## О программе
_Проект YaMDb собирает отзывы пользователей на произведения. Возможно разделение произведений по категориям и жанрам. Новые жанры может создавать только администратор. Пользователи могут оставить к произведениям текстовые отзывы и поставить произведению оценку._
## Используемые технологии
1. Gunicorn
2. Nginx
3. Docker
4. Docker-compose
5. PostgreSQL

## Разработчики
***
В работе над программой принимали участие следующие замечательные люди:

1. Антон Гришин Тимлид, модуль по работе с пользователями и модуль аутентификации / регистрации
2. Павел Фаниев Модуль по работе со справочником произведений, жанров и категорий
3. Никита Сморчков Модуль по работе с отзывами и комментариями

***

## Шаблон файла .env
***
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY = ваш секретный ключ
DEBUG = False
ALLOWED_HOSTS = *
```
***
## Запуск контейнера и приложкний  в нем
__Перейдите в репозиторий для запуска Docker__
```
cd infra/
```
__Запустите docker-compose__
```
docker-compose up
```
__Выполните миграции__
```
docker-compose exec web python manage.py migrate
```
__Создайте суперпользователя__
```
 docker-compose exec web python manage.py createsuperuser - для ОС Linux
 winpty docker-compose exec web python manage.py createsuperuser - для ОС Windows
```
__Загрузите статику__
```
docker-compose exec web python manage.py collectstatic --no-input - для ОС Linux
winpty docker-compose exec web python manage.py collectstatic --no-input для ОС Windows
```
__При необходимости создайте резервную копию БД__
```
 docker-compose exec web python manage.py dumpdata > fixtures.json
```

__Проект доступен по ссылками__
```
130.193.53.238/admin/
```
```
130.193.53.238/redoc/
```

https://github.com/Pavel-Faniev/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg
