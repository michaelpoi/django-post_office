"""
Only define the tasks and handler if we can import celery.
This allows the module to be imported in environments without Celery, for
example by other task queue systems such as Huey, which use the same pattern
of auto-discovering tasks in "tasks" submodules.
"""

import datetime
import logging
import time

from django.utils.timezone import now

from post_office.mail import _send_bulk, get_queued
from post_office.utils import cleanup_expired_mails
from .dblock import db_lock, TimeoutException, LockedException
from django.db import connection as db_connection
from django.db import transaction

from .settings import get_celery_enabled

try:
    if get_celery_enabled():
        from celery import shared_task
    else:
        raise NotImplementedError()
except (ImportError, NotImplementedError):

    def queued_mail_handler(sender, **kwargs):
        """
        To be called by :func:`post_office.signals.email_queued.send()` for triggering asynchronous
        mail delivery – if provided by an external queue, such as Celery.
        """
else:

    @shared_task(ignore_result=True)
    def send_queued_mail(*args, **kwargs):
        """
        To be called by the Celery task manager.
        """

        while True:
            queued_emails = get_queued().select_for_update(of=('self',), skip_locked=True)
            with transaction.atomic():
                try:
                    _send_bulk(queued_emails, uses_multiprocessing=False)
                except Exception as e:
                    raise e

                if not get_queued().select_for_update(of=('self',), skip_locked=True).exists():
                    break
            db_connection.close()


    def queued_mail_handler(sender, **kwargs):
        """
        Trigger an asynchronous mail delivery.
        """
        print(sender)
        send_queued_mail.delay()


    @shared_task(ignore_result=True)
    def cleanup_mail(*args, **kwargs):
        days = kwargs.get('days', 90)
        cutoff_date = now() - datetime.timedelta(days)
        delete_attachments = kwargs.get('delete_attachments', True)
        cleanup_expired_mails(cutoff_date, delete_attachments)
