import os
from pathlib import Path

# Базовый каталог проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ (замените на свой в продакшне)
SECRET_KEY = 'django-insecure-8*b!lvk*=yc9)_vojo*c_+@b++*4i&pwr(jwr98*grllz7@uk_'

# Режим отладки (в продакшне установите False)
DEBUG = True

# Разрешенные хосты (в продакшне укажите ваши домены)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.6',  # Замените на ваш локальный IP
]

# Установленные приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'sslserver',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_extensions',
    'django.contrib.sessions',
    'daphne',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # Ваше основное приложение
    'channels',  # Для WebSocket
    'django.contrib.sites',
]

# Промежуточные слои
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Корневой URL-конфиг
ROOT_URLCONF = 'job_platform.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI-приложение
WSGI_APPLICATION = 'job_platform.wsgi.application'

ASGI_APPLICATION = 'job_platform.asgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",  # для локальной разработки
        # Для продакшна используйте Redis:
        # "BACKEND": "channels_redis.core.RedisChannelLayer",
        # "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    },
}

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Интернационализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Статические файлы (CSS, JavaScript, изображения)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'core/static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Медиафайлы (загруженные пользователями)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Настройки аутентификации
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_REDIRECT_URL = 'home'



# Настройки сессий
SESSION_COOKIE_AGE = 1209600  # 2 недели (в секундах)

# Настройки кэширования (для продакшна используйте Redis или Memcached)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Настройки логгирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Настройки для файлов cookie (в продакшне используйте HTTPS)
CSRF_COOKIE_SECURE = False  # В продакшне установите True
SESSION_COOKIE_SECURE = False  # В продакшне установите True

# Настройки для статических файлов (в продакшне)
if not DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    'https://your-domain.com',
    'https://192.168.1.6'
]


# Настройки почты (MailHog для локальной разработки)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'       # MailHog работает на localhost
EMAIL_PORT = 1025             # Порт по умолчанию для MailHog
EMAIL_USE_TLS = False         # Не используем TLS для локального тестирования
EMAIL_HOST_USER = ''          # Не требуется для MailHog
EMAIL_HOST_PASSWORD = ''      # Не требуется для MailHog
DEFAULT_FROM_EMAIL = 'no-reply@jobplatform.local'  # Отображаемый email отправителя

"""
Для работы в продакшене используйте реальный SMTP-сервер:

# Пример для Gmail:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ваш@gmail.com'
EMAIL_HOST_PASSWORD = 'пароль-приложения'
DEFAULT_FROM_EMAIL = 'ваш@gmail.com'

# Пример для Yandex:
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'ваш@yandex.ru'
EMAIL_HOST_PASSWORD = 'пароль-приложения'
"""

# Настройки аутентификации
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Настройки подтверждения email
SITE_ID = 1  # Обязательно для работы с email
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[JobPlatform] '

# URL-адреса
PASSWORD_RESET_TIMEOUT = 86400  # 24 часа в секундах


if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    
    
SITE_NAME = 'Job Platform'

# Email отправителя
DEFAULT_FROM_EMAIL = 'noreply@jobplatform.example.com'

PEERJS_HOST = 'localhost'
PEERJS_PORT = 9000
PEERJS_PATH = '/peerjs'


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Настройки для работы с самоподписными сертификатами
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://localhost:8000']

# Для django-extensions (runserver_plus)
