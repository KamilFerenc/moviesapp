# moviesapp

Moviesapp is Django REST API app which allows to retrieve data about movies from external OMDBapi. The requested movie is saved in database. Movies can be commented by users. [kamilferenc-moviesapp](https://kamilferencmoviesapp.herokuapp.com/)  

## Features

### Movies 
#### POST method:
- Request body requires the movie title,
- The request body (Title) is validated, in case of empty request body it returns Error - 400 and message,
- The requested movie is checked if already exists in database. If not and data can be serialized correctly movie object is saved in database and returned as response.

#### GET method
##### List all movies in database
- All movies are returned in response, and contain all data from OMDb,
- Extra data: url to particular movie, date of save movie object in database,
- Extra functionalities: - pagination(default 5 - per page), sorting (Year, Title, Genre) and ordering (Year, Title).
#### Movie detail 
- Return all movie's data in response.

### Comments
#### POST method:
- Required: user, comment, movie(id). Date of creation is set as auto_add_now=True in models,
- The request body is validated - in case no error, comment is saved in database and returned as response.
#### GET method
##### List all comments in database
- All comments are returned in response,
- Extra data: user name, the url to movie which has been commented,
- Extra functionalities - pagination(default: 10 - per page), sorting (movie id, user) and ordering (movie, user, created).

### Top commented movies
#### GET method
- Returns all movies existing in database in descending order 'total comments',
- If date range hasn't been specified, ranking is based on all existing comments.


### Project details
##### Third-Party Libraries 
- django-filter - useful library to filtering objects,
- pytes - tool for testing application, useful interface coverage-report,
- mixer - tool used in order to generate object and save them in database during tests.

##### Test
- Project contain basic tests, 
- Used APIRequestFactory() in order to test all functionalities,
- Coverage = 99%

##### Pre requisites
- Django 2.1.7
- Django Rest Framework 3.9.4
- Python 3.6.7
- PostgreSQL 10.6
- psycopg2 2.8.2

##### Setup

- Install Python 3.6.7
- Install PostgreSQL 10.6
- Create Database - PostgreSQL (required - database(name), user(name), password(name))
- ```$ mkdir project```
- ```$ cd project```
- Create new virtual environment
- Clone repository ```git clone https://github.com/KamilFerenc/moviesapp.git```
- ```$ cd moviesapp```
- ```pip install -r requirements.txt```
Change file ```settings.py```:
- Change database settings
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database(name)',
        'USER': 'user(name)',
        'PASSWORD': 'user(password)',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
```
- Change OMDb 

```
# OMDb parameters
OMDb_API_KEY = 'you-api-key'
```
- 
- Run command: ```python manage.py migrate```
- Run command: ```python manage.py runserver```
- Open web browser at address ```http://127.0.0.1:8000/```

- To run tests enter ```pytest```

##### Endpoint:
###### Movies
- ```GET /movies/```
- ```GET /movies/?ordering=Year```
- ```GET /movies/?ordering=Title```
- ```GET /movies/?Title__icontains=title&Year=&Year__gt=&Year__lte=&Genre__icontains=```

-  ```POST /movies/```  ```{"Title": "movie title"} - required```
###### Comments
- ```GET /comments/```
- ```GET /comments/?ordering=movie```
- ```GET /comments/?ordering=user```
- ```GET /comments/?ordering=created```
- ```GET /comments/?movie=:id&user=:str```
-  ```POST /comments/```
```{"user": "user name", "comment": "comment text", "movie": "movie id: int"} - required```
###### Top comments
- ```https://kamilferencmoviesapp.herokuapp.com/top/```
- ```https://kamilferencmoviesapp.herokuapp.com/top/?since=YYYY-M-D&to=YYYY-M-D```