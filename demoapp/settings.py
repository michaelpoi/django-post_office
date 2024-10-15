"""
Django settings for demoapp project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import sys
from pathlib import Path
# from dotenv import load_dotenv
import os
from django.utils.translation import gettext_lazy as _

# load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'secret_key'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'storages',
    'ckeditor',
    'ckeditor_uploader',
    'post_office',
]

USE_S3 = False
if USE_S3:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "endpoint_url": 'http://138.232.3.68:9000',  # Note the lowercase 'endpoint_url'
                'access_key': 'minioadmin',
                'secret_key': 'minioadmin',
                'bucket_name': 'media',
                'querystring_auth': False,
                'use_ssl': False,  # Set this to True if you use HTTPS
                'file_overwrite': False,  # Optional: set to False to avoid overwriting files with the same name
            },
        },
        'staticfiles': {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "endpoint_url": 'http://138.232.3.68:9000',  # Note the lowercase 'endpoint_url'
                'access_key': 'minioadmin',
                'secret_key': 'minioadmin',
                'bucket_name': 'static',
                'querystring_auth': False,
                'use_ssl': False,  # Set this to True if you use HTTPS
                'file_overwrite': False,  # Optional: set to False to avoid overwriting files with the same name
            },
        },
        'post_office_attachments': {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "endpoint_url": 'http://138.232.3.68:9000',
                'access_key': 'minioadmin',
                'secret_key': 'minioadmin',
                'bucket_name': 'attachments',
                'querystring_auth': True,
                'use_ssl': False,
                'file_overwrite': False,
            }
        }
    }
    MEDIA_URL = f"http://138.232.3.68:9000/media/"
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'workdir' / 'media'
    STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files settings

# Set MEDIA_URL for media files


# MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'
# MEDIA_ROOT = BASE_DIR / 'workdir' / 'media'

CKEDITOR_UPLOAD_PATH = 'ckeditor_uploads'

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('de', 'German'),
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'new_post_office',  # Your database name
        'USER': 'post_office',  # Your database user
        'PASSWORD': 'post_office',  # Your database password
        'HOST': 'localhost',  # Or the database server's IP address
        'PORT': '5432',  # Default PostgreSQL port
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

USE_TZ = False
# POST_OFFICE_CACHE = False


MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'demoapp.middleware.AutoLoginMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

ROOT_URLCONF = 'demoapp.urls'

SILENCED_SYSTEM_CHECKS = ['admin.E408']

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'
#CELERY_ENABLED = True
EMAIL_BACKEND = 'post_office.EmailBackend'
# EMAIL_HOST = 'smtp.mailgun.org'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'postmaster@sandboxf099cc52e4d94225bf3ad0e9f2bcabd2.mailgun.org'
# EMAIL_HOST_PASSWORD = '722eddd8ef922dbcd381d68f6b28c4f0-7a3af442-a4d621a6'

EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'default@email.com'
# EMAIL_HOST_USER = 'test'
# EMAIL_HOST_PASSWORD = 'test'
#print(EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

TEMPLATES = [
    {
        'BACKEND': 'post_office.template.backends.post_office.PostOfficeTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR / 'demoapp' / 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
            ]
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

POST_OFFICE = {
    'TEMPLATE_ENGINE': 'post_office',
    'CELERY_ENABLED': True,
    'MAX_RETRIES': 3,
    'BATCH_SIZE': 20,
    'BATCH_DELIVERY_TIMEOUT': 30,
    'MESSAGE_ID_ENABLED': True,
    'DEFAULT_PRIORITY': 'medium',
    'BACKENDS': {
        'default': 'django.core.mail.backends.smtp.EmailBackend',
        'ses': 'django_ses.SESBackend'
    },
    'BASE_FILES': [
        ('/home/mykhailo/Desktop/emails/django-post_office/demoapp/templates/email/default.html', _('Default')),
        ('email/placeholders.html', _('Placeholders')),
        ('/home/mykhailo/Desktop/out.html', _('Out')),
    ]
}
WSGI_APPLICATION = "demoapp.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/


TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


# Celery - prefix with CELERY_
CELERY_BROKER_URL = "redis://localhost:6379/"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter',
             'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['Image'],
            ['Format']  # Adding headers (e.g., Heading 1, Heading 2, etc.)
        ],
        'format_tags': 'p;h1;h2;h3;pre',  # Define the available formats (headers and others)
        'width': 1000
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',  # Use the appropriate Redis server URL
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
