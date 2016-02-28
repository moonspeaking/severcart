# -*- coding:utf-8 -*-

import os

DJ_PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(DJ_PROJECT_DIR)
WSGI_DIR = os.path.dirname(BASE_DIR)
REPO_DIR = os.path.dirname(WSGI_DIR)
DATA_DIR = os.environ.get('OPENSHIFT_DATA_DIR', BASE_DIR)



DEBUG = True

DEMO  = True

ALLOWED_HOSTS = ['*']


SECRET_KEY = os.getenv('OPENSHIFT_SECRET_TOKEN')
# Application definition

INSTALLED_APPS = (
#    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'index',
    'mptt',
    'accounts',
    'events',
    'docs',
    'reports',
    'service',
)

WSGI_APPLICATION = 'newskald_ru.wsgi_shift.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'py',
        'USER': os.getenv('OPENSHIFT_POSTGRESQL_DB_USERNAME'),
        'PASSWORD': os.getenv('OPENSHIFT_POSTGRESQL_DB_PASSWORD'),
        'HOST': os.getenv('OPENSHIFT_POSTGRESQL_DB_HOST'),
        'PORT': os.getenv('OPENSHIFT_POSTGRESQL_DB_PORT'),
    }
}

if DEBUG:
    STATICFILES_DIRS = (os.path.join(os.getenv('OPENSHIFT_REPO_DIR'), 'wsgi', 'static'),)
    MEDIAFILES_DIRS = (os.path.join(os.getenv('OPENSHIFT_REPO_DIR'), 'wsgi', 'media'),)


STATIC_ROOT_CSV = os.path.join(os.getenv('OPENSHIFT_REPO_DIR'), 'wsgi', 'static', 'csv')
MAX_COUNT_CSV_FILES = 20


STATIC_ROOT_DOCX = os.path.join(os.getenv('OPENSHIFT_REPO_DIR'), 'wsgi', 'static', 'docx')
MAX_COUNT_DOCX_FILES = 20

# for collect static utility
STATIC_ROOT = os.path.join(WSGI_DIR, 'static')

STATIC_URL = '/static/'
MEDIA_URL = '/media/'