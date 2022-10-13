# foodgram
Приложение «Продуктовый помощник»: сайт, на котором пользователи  
будут публиковать рецепты, добавлять чужие рецепты в избранное и  
подписываться на публикации других авторов. Сервис «Список покупок»  
позволит пользователям создавать список продуктов, которые нужно купить  
для приготовления выбранных блюд. 

### Стэк технологий:
python 3.10  
django 4.1.2  
djangorestframework 3.14.0  
gunicorn 20.0.4  
nginx  
postgres 14.5  
docker-compose 3.3

### Как запустить проект:

Клонировать репозиторий:

```
git clone git@github.com:vkirikv/foodgram-project-react.git
```

Перейти в папку foodgram-project-react/infra и запустить docker-compose:

```
docker-compose up
```

Выполнить миграции:

```
docker-compose exec web python manage.py migrate
```

```
docker-compose exec web python manage.py createsuperuser
```

```
docker-compose exec web python manage.py collectstatic --no-input 
```


#### Готовый проект
Готовое приложение можно посмотреть перейдя по [этой ссылке](http://178.154.222.19/).

### Автор проекта:
Владимир Кириллов  


![foodgram_workflow](https://github.com/vkirikv/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)