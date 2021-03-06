# -*- coding:utf-8 -*-

VERSION = '0.7.6'



# отключаем показ ссылок на домашнюю страницу, техподдержку, логотип
SHOW_COPYRIGHT = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.join(BASE_DIR, 'conf'))

# автоматический переключатель продакшена и девелопмента
from settings_dev import *

ALLOWED_HOSTS = ['*']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# Application definition

INSTALLED_APPS = (
#    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'debug_toolbar',
    'pytz',
    'index',
    'mptt',
    'accounts',
    'events',
    'docs',
    'reports',
    'service',
    'search',
    'storages',
    'dhtml',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # автоматический выбор языка
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # установка языка интерфейса на основе сессии
    'plugins.middleware.InsertVarToRequest',
)

#список поддерживаемых языков
LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
]

ROOT_URLCONF = 'conf.urls'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
    }
}


SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# включаем кэширование шалонов.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
#                   'django.core.context_processors.static',
                'django.template.context_processors.static',
            ],
            'loaders':[
                ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'), )

AUTH_USER_MODEL = 'accounts.AnconUser'
AUTHENTICATION_BACKENDS = ['accounts.backends.UserAuthBackend', ]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s [%(pathname)s:%(lineno)s] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'comp': {
            'handlers': ['debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'simp': {
            'handlers': ['info_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'handlers': {
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR + '/logs/debug.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 7,
            'encoding': 'utf-8',
            'formatter': 'verbose',
        },
        'info_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR + '/logs/debug.log',
            'encoding': 'utf-8',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 7,
            'formatter': 'simple',
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        #'mail_admins': {
        #    'level': 'ERROR',
        #    'class': 'django.utils.log.AdminEmailHandler',
        #    'filters': ['verbose']
        #}

    },
}

LOGIN_URL = '/auth/login/'

MAX_EVENT_LIST = 16
DASHBOARD_EVENT_LIST = 11

# Настройки шаблона docx файла
MAX_TABLE_ROWS_FIRST_PAGE = 30 # должен резервировать место для шапки акта

MAX_TABLE_ROWS = 40

HISTORY_LENGTH = 5

SHOW_HELP = False

HOME_SITE = 'http://www.severcart.org'

# длина символов в номере РМ, после которых будет производиться 
# усечение 
TRLEN = 9
