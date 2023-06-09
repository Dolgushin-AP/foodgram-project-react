## Описание проекта
[![YaMDb workflow](https://github.com/Dolgushin-AP/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/Dolgushin-AP/foodgram-project-react/actions/workflows/main.yml) <br>
***- Foodgram, «Продуктовый помощник»***
Foodgram - это онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд..

## Инструкции по установке

***- Клонируйте репозиторий:***
```
git clone https://github.com/Dolgushin-AP/foodgram-project-react.git
```

***- Установите и активируйте виртуальное окружение:***
- для MacOS
```
python3 -m venv venv
```
- для Windows
```
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
```

***- Установите зависимости из файла requirements.txt:***
```
pip install -r requirements.txt
```

***- Примените миграции:***
```
python manage.py migrate
```

***- В папке foodgram выполните команду для запуска локально:***
```
python manage.py runserver
```
***- Локально документация доступна по адресу:***
```
http://localhost/api/docs/
```
## Локально проект доступен по ссылкам:

http://127.0.0.1:8000/admin/ <br>
http://127.0.0.1:8000/api/ <br>
http://127.0.0.1:8000/api/recipes/ <br>
http://127.0.0.1:8000/api/users/ <br>
http://127.0.0.1:8000/api/tags/ <br>
http://127.0.0.1:8000/api/ingredients/ <br>

### Деплой:
Установить и запустить Docker Desktop

Запуск контейнеров:
```
docker compose up -d --build
```

Заполнение .env по шаблону:
```
DB_ENGINE=django.db.backends.postgresql
```
```
DB_NAME=postgres
```
```
POSTGRES_USER=postgres
```
```
POSTGRES_PASSWORD=postgres
```
```
DB_HOST=db
```
```
DB_PORT=5432
```
Создание суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```

## Развёрнутый проект после деплоя доступен по ссылкам:

http://84.201.178.118/recipes/ <br>
http://84.201.178.118/subscriptions/ <br>
http://84.201.178.118/admin/ <br>
http://84.201.178.118/api/docs/ <br>

Данные юзера-админа:
```
Имя: Anton
Фамилия: Dolgushin
Имя пользователя: shell
Адрес электронной почты: russhell@yandex.ru
Пароль: derparole
```

Автор разделов backend и deploy - Долгушин А.П.
