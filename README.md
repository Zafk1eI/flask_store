

## Installation

Установить проект можно при помощи:

```bash
  npm install # установка tailwind
  pip install -r requirements.txt
```

## Configuration

Cоздайте config.py. Пример:
    
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