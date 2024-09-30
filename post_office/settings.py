from pathlib import Path
import warnings
from django.template import loader

from django.conf import settings
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.mail.utils import DNS_NAME
from django.template import engines as template_engines


import datetime


def get_email_templates():
    templates_settings = getattr(settings, 'TEMPLATES', {})
    template_dirs = []
    for template_set in templates_settings:
        template_dirs.extend([Path(path) / 'email' for path in template_set['DIRS']])

    template_choices = []

    for template_dir in template_dirs:
        if template_dir.exists() and template_dir.is_dir():
            for file_path in template_dir.rglob('*.html'):
                relative_path = file_path.relative_to(template_dir.parent)
                template_choices.append((str(relative_path), str(relative_path)))

    return template_choices


def get_template(template_name):
    return loader.get_template(template_name)


def get_backend(alias='default'):
    return get_available_backends()[alias]


def get_available_backends():
    """Returns a dictionary of defined backend classes. For example:
    {
        'default': 'django.core.mail.backends.smtp.EmailBackend',
        'locmem': 'django.core.mail.backends.locmem.EmailBackend',
    }
    """
    backends = get_config().get('BACKENDS', {})

    if backends:
        return backends

    # Try to get backend settings from old style
    # POST_OFFICE = {
    #     'EMAIL_BACKEND': 'mybackend'
    # }
    backend = get_config().get('EMAIL_BACKEND')
    if backend:
        warnings.warn('Please use the new POST_OFFICE["BACKENDS"] settings', DeprecationWarning)

        backends['default'] = backend
        return backends

    # Fall back to Django's EMAIL_BACKEND definition
    backends['default'] = getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

    # If EMAIL_BACKEND is set to use PostOfficeBackend
    # and POST_OFFICE_BACKEND is not set, fall back to SMTP
    if 'post_office.EmailBackend' in backends['default']:
        backends['default'] = 'django.core.mail.backends.smtp.EmailBackend'

    return backends


def get_cache_backend():
    if hasattr(settings, 'CACHES'):
        if 'post_office' in settings.CACHES:
            return caches['post_office']
        else:
            # Sometimes this raises InvalidCacheBackendError, which is ok too
            try:
                return caches['default']
            except InvalidCacheBackendError:
                pass
    return None


def get_config():
    """
    Returns Post Office's configuration in dictionary format. e.g:
    POST_OFFICE = {
        'BATCH_SIZE': 1000
    }
    """
    return getattr(settings, 'POST_OFFICE', {})


def get_languages_list():
    lang_conf = getattr(settings, 'LANGUAGES', [])
    return [lang[0] for lang in lang_conf]


def get_default_language():
    return settings.LANGUAGE_CODE


def get_batch_size():
    return get_config().get('BATCH_SIZE', 100)


def get_celery_enabled():
    return get_config().get('CELERY_ENABLED', False)


def get_lock_file_name():
    return get_config().get('LOCK_FILE_NAME', 'post_office')


# def get_threads_per_process():
#     return get_config().get('THREADS_PER_PROCESS', 5)


def get_default_priority():
    return get_config().get('DEFAULT_PRIORITY', 'medium')


def get_log_level():
    return get_config().get('LOG_LEVEL', 2)


def get_sending_order():
    return get_config().get('SENDING_ORDER', ['-priority'])


def get_template_engine():
    using = get_config().get('TEMPLATE_ENGINE', 'django')
    return template_engines[using]


def get_override_recipients():
    return get_config().get('OVERRIDE_RECIPIENTS', None)


def get_max_retries():
    return get_config().get('MAX_RETRIES', 0)


def get_retry_timedelta():
    return get_config().get('RETRY_INTERVAL', datetime.timedelta(minutes=15))


def get_message_id_enabled():
    return get_config().get('MESSAGE_ID_ENABLED', False)


def get_message_id_fqdn():
    return get_config().get('MESSAGE_ID_FQDN', DNS_NAME)


# BATCH_DELIVERY_TIMEOUT defaults to 180 seconds (3 minutes)
def get_batch_delivery_timeout():
    return get_config().get('BATCH_DELIVERY_TIMEOUT', 180)
