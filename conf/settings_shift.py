# -*- coding:utf-8 -*-

import os, json

DJ_PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(DJ_PROJECT_DIR)
WSGI_DIR = os.path.dirname(BASE_DIR)
REPO_DIR = os.path.dirname(WSGI_DIR)
DATA_DIR = os.environ.get('OPENSHIFT_DATA_DIR', BASE_DIR)

import sys
sys.path.append(os.path.join(REPO_DIR, 'libs'))


json_data=open(os.path.join(DATA_DIR, 'secrets.json')).read()

SECRETS = json.loads(json_data)

DEBUG = False

DEMO  = True

ALLOWED_HOSTS = ['*']


SECRET_KEY = SECRETS['secret_key']

WSGI_APPLICATION = 'conf.wsgi_shift.application'

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


STATIC_ROOT_CSV = os.path.join(WSGI_DIR, 'static', 'csv')
MAX_COUNT_CSV_FILES = 20

STATIC_ROOT_DOCX = os.path.join(WSGI_DIR, 'static', 'docx')
MAX_COUNT_DOCX_FILES = 20

STATIC_ROOT_PDF = os.path.join(BASE_DIR, 'static', 'pdf')
MAX_COUNT_PDF_FILES = 20

# for collect static utility
STATIC_ROOT = os.path.join(WSGI_DIR, 'static')

STATIC_URL = '/static/'
