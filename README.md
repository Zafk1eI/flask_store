# flask-store

## Git clone

```bash
git clone <URL_репозитория>
cd <название_папки_проекта> # при необходимости
```
## Installation

Установить проект можно при помощи:

```bash
  python -m venv venv
  venv\Scripts\activate # активация вирт. окружения
  npm install # установка tailwind
  pip install -r requirements.txt
```

## Configuration

Создайте config.py. Пример:
    
```bash
  class Config:
    SECRET_KEY = 'SECRET_KEY'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'mysql://user:password@localhost/db_name')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ADMIN_SWATCH = 'cerulean'
```
## Run Flask

```bash
python app.py
```