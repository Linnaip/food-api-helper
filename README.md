# praktikum_new_diplom
Запуск проекта
1. Скронируйте репозиторий на локальную машину:
```
git@github.com:Linnaip/foodgram-project-react.git
```
2. Создайте .env файл в директории backend/foodgram/, в котором должны содержаться следующие переменные для подключения к базе PostgreSQL:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
3. Перейдите в директорию infra/ и выполните команды:
```
sudo docker-compose up -d --build
```
```
В Windows команда выполняется без sudo
```
4. В контейнере backend выполните команды:
```
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input 
```
Загрузите в бд ингредиенты командой ниже.
```

```
### Ссылка на развернутый проект:
```
http://projectlinnaip.ddns.net
```
Доступные адреса проекта:
```
http://localhost/ - главная страница сайта;
http://localhost/admin/ - админ панель;
http://localhost/api/ - API проекта
http://localhost/api/docs/redoc.html - документация к API
```
### Автор
```
Лычагин Андрей (Github - Linnaip)
```
