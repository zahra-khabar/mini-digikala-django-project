from .base import *
from decouple import config


DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
    }
}