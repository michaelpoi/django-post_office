from datetime import timedelta

from django.conf import settings as django_settings
from django.core.mail.utils import DNS_NAME


class Settings:
    @property
    def POST_OFFICE(self):
        config = getattr(django_settings, 'POST_OFFICE', {})
        config.setdefault('BATCH_SIZE', 100)
        config.setdefault('CELERY_ENABLED', False)
        config.setdefault('DEFAULT_PRIORITY', 'medium')
        config.setdefault('LOG_LEVEL', 'medium')
        config.setdefault('SENDING_ORDER', ['-priority'])
        config.setdefault('TEMPLATE_ENGINE', 'django')
        config.setdefault('OVERRIDE_RECIPIENTS', None)
        config.setdefault('MAX_RETRIES', 0)
        config.setdefault('RETRY_INTERVAL', timedelta(minutes=15))
        config.setdefault('MESSAGE_ID_ENABLED', True)
        config.setdefault('MESSAGE_ID_FQDN', DNS_NAME)
        return config

    @property
    def CKEDITOR_CONFIGS(self):
        config = getattr(django_settings, 'CKEDITOR_CONFIGS', {})
        config.setdefault('default', {
                    'toolbar': 'Basic',
                    'toolbar_Basic': [
                        ['Bold', 'Italic'],
                        ['NumberedList', 'BulletedList'],
                        ['Link', 'Unlink'],
                        ['RemoveFormat'],
                    ],
                    'height': 200,
                    'width': '100%',
                    'removePlugins': 'sourcearea,anchor,image',
                })

        return config


settings = Settings()
