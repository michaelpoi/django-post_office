# Django Post Office

**Asynchronous email sending library for Django with enhanced templating options.**

post_office provides a set of powerful features, such as:

- Handling millions of emails efficiently. 
- Allows you to send emails asynchronously.
- Multi backend support. 
- Support for inlined images.
- 2-phase email templating to allow non-technical users contributing to emails creation.
- Scheduling support.
- Works with task queues like RQ and Celery.
- Uses multiprocessing to send emails in parallel.

## Dependencies

- [django \>= 2.2](https://djangoproject.com/)
- [django-ckeditor](https://pypi.org/project/django-ckeditor/)
- [nh3](https://pypi.org/project/nh3/)
- [lxml](https://pypi.org/project/lxml/)

Installing nh3 is strongly encouraged for security reasons. Only with installed nh3 emails will be rendered in admin interface.

## Installation

[![Build Status](https://github.com/ui/django-post_office/actions/workflows/test.yml/badge.svg)](https://github.com/michaelpoi/django-post_office/actions)
[![PyPI](https://img.shields.io/pypi/pyversions/django-post_office.svg)]()
[![PyPI version](https://img.shields.io/pypi/v/django-post_office.svg)](https://pypi.python.org/pypi/django-post_office)
[![PyPI](https://img.shields.io/pypi/l/django-post_office.svg)]()


```sh
pip install django-post_office
```

Add post_office and ckeditor to your installed app in settings.py:

```python
INSTALLED_APPS = [
# other apps,
'ckeditor',
'ckeditor_uploader',
'post_office',
]
```

To your settings.py also add email server configurations:

```python
EMAIL_HOST = '<your-smtp-host.com>'
EMAIL_PORT = '<SMTP-PORT>'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'default@email.com'
```

To your list of template engines (`TEMPLATES`) settings add a special template backend:
```python
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
]
```
Add `CKEDITOR_UPLOAD_PATH`. This path will be used to store ckeditor uploaded images inside `MEDIA_ROOT`:

```python
CKEDITOR_UPLOAD_PATH = 'ckeditor_uploads'
```

Add `STATIC_URL` and `STATIC_ROOT`

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

Add `MEDIA_URL` and `MEDIA_ROOT`

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'workdir' / 'media'
```

Run `migrate`:

```shell
python manage.py migrate
```

Run `collectstatic`:

```shell
python manage.py collectstatic
```

Set `post_office.EmailBackend` as your `EMAIL_BACKEND` in Django's `settings.py`:

```python
EMAIL_BACKEND = 'post_office.EmailBackend'
```

## Quickstart

Send a simple email is really easy:

```python
from post_office import mail

mail.send(
    'recipient@example.com', # List of email addresses also accepted
    'from@example.com',
    subject='My email',
    message='Hi there!',
    html_message='Hi <strong>there</strong>!',
)
```

If you want to use templates:

- In your templates folder create an .html file with your email markup. Inside it you can leave placeholders or use context vars. For example something like this:

```html
{% load post_office %}

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">#var#
    <title>Example email template</title>
</head>
<body>
    Hello, {{ username }}
    {% placeholder 'main' %}
</body>
</html>
```

- Register your template in `settings.py`:

```python
POST_OFFICE = {
    'BASE_FILES': [
        ('your-file/path', _('Your-Name')),
    ]
}
```

You can use relative path from your `templates` folder or absolute file path.

- Open your admin interface and create a new Email Template instance:
    - Enter name. This will be used as identifier for your template and click “Save and continue editing”.
    - Select Base File which you have created.
    - You will be requested to enter values to the placeholders you entered in the template. (main in the example).
        You can specify variables to be filled with the context.
        Syntax is `#var#`.
        Example: This is a simple mail created by #generator#
    - If you have more than 1 language configured you will be requested to fill values for all languages in `LANGUAGES`.
    - Save your instance.
- To send an email with the created template:

```python
from post_office import mail

mail.send(
    'recipient@example.com', # List of email addresses or list of EmailAddress also accepted
    'from@example.com',
    template='your-template-here', # Could be an EmailTemplate instance or name
    context={'generator': 'post_office',
    'username': 'michaelpoi',}, # Context is used to fill both {{ var }} in html and #var# in ckeditor.
    language='en' # If not specified settings.LANGUAGE_CODE is used
)
```

The above command will put your email on the queue so you can use the command in your webapp without slowing down the request/response cycle too much. 
To actually send them out, run python manage.py send_queued_mail. 
You can schedule this management command to run regularly via cron:

```shell
* * * * * (/usr/bin/python manage.py send_queued_mail >> send_mail.log 2>&1)
```

Full documentation can be found [here](https://docs_link.com)