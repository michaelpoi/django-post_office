Installation
=========================

``pip install post_office``

Add ``post_office`` and ``ckeditor`` to your installed app in ``settings.py``:

.. code-block::

    INSTALLED_APPS = [
    # other apps,
    'ckeditor',
    'ckeditor_uploader',
    'post_office',
    ]

To your ``settings.py`` also add email server configurations:

.. code-block::

    EMAIL_HOST = '<your-smtp-host.com>'
    EMAIL_PORT = <SMTP port>
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'default@email.com'

To your list of template engines (``TEMPLATES``) settings add a special template backend:

.. code-block::

    TEMPLATES = [
    {
        'BACKEND': 'post_office.template.backends.post_office.PostOfficeTemplates',
        'APP_DIRS': True,
        'DIRS': [BASE_DIR / 'templates', ...],
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
    ...

Add ``CKEDITOR_UPLOAD_PATH``. This path will be used to store ckeditor uploaded images inside ``MEDIA_ROOT``:

.. code-block::

    CKEDITOR_UPLOAD_PATH = 'ckeditor_uploads'

Add ``STATIC_URL`` and ``STATIC_ROOT``

.. code-block::

    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'

Add ``MEDIA_URL`` and ``MEDIA_ROOT``

.. code-block::

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'workdir' / 'media'

Run ``migrate``:

.. code-block::

    python manage.py migrate

Run ``collectstatic``:

.. code-block::

    python manage.py collectstatic

Set ``post_office.EmailBackend`` as your ``EMAIL_BACKEND`` in django's ``settings.py``:

.. code-block::

    EMAIL_BACKEND = 'post_office.EmailBackend'


