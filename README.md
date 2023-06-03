## Описание проекта
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
```
- http://127.0.0.1:8000/admin/
- http://127.0.0.1:8000/api/
- http://127.0.0.1:8000/api/recipes/
- http://127.0.0.1:8000/api/users/
- http://127.0.0.1:8000/api/tags/
- http://127.0.0.1:8000/api/ingredients/
```
