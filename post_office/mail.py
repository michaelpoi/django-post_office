from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection as db_connection
from django.db.models import Q
from django.template import Context, Template
from django.utils import timezone
from email.utils import make_msgid
from multiprocessing import Pool

from .connections import connections
from .dblock import db_lock, TimeoutException, LockedException
from .logutils import setup_loghandlers
from .models import EmailModel, EmailMergeModel, Log, PRIORITY, STATUS, Recipient
from .settings import (
    get_available_backends,
    get_batch_delivery_timeout,
    get_batch_size,
    get_log_level,
    get_max_retries,
    get_message_id_enabled,
    get_message_id_fqdn,
    get_retry_timedelta,
    get_sending_order, get_default_language, get_languages_list,
)
from .signals import email_queued
from .utils import (
    create_attachments,
    get_email_template,
    parse_emails,
    parse_priority,
    split_emails, get_recipients_objects, render_email_template, render_message, set_recipients, get_or_create_recipient
)

logger = setup_loghandlers('INFO')


def create(
        sender,
        recipients=None,
        cc=None,
        bcc=None,
        subject='',
        message='',
        html_message='',
        context=None,
        scheduled_time=None,
        expires_at=None,
        headers=None,
        template=None,
        priority=None,
        render_on_delivery=False,
        commit=True,
        backend='',
        language='',
):
    """
    Creates an email from supplied keyword arguments. If template is
    specified, email subject and content will be rendered during delivery.
    """
    priority = parse_priority(priority)
    status = None if priority == PRIORITY.now else STATUS.queued

    if recipients is None:
        recipients = []
    if cc is None:
        cc = []
    if bcc is None:
        bcc = []
    if context is None:
        context = {}
    message_id = make_msgid(domain=get_message_id_fqdn()) if get_message_id_enabled() else None
    recipients_addresses = get_recipients_objects(recipients)
    cc_addresses = get_recipients_objects(cc)
    bcc_addresses = get_recipients_objects(bcc)
    # If email is to be rendered during delivery, save all necessary
    # information
    if render_on_delivery:
        email = EmailModel(
            from_email=sender,
            scheduled_time=scheduled_time,
            expires_at=expires_at,
            message_id=message_id,
            headers=headers,
            priority=priority,
            status=status,
            context=context,
            template=template,
            backend_alias=backend,
        )

        if commit:
            email.save()
            set_recipients(email, recipients_addresses, cc_addresses, bcc_addresses)


    else:

        if not context.get('recipient', None):
            context['recipient'] = get_or_create_recipient(recipients[0])

        print(context)
        if template:
            subject = template.subject
            message = template.content
            recipient_context = context.get('recipient', None)
            html_message = render_email_template(template, recipient_context, language=language)

        subject = render_message(subject, context)
        message = render_message(message, context)
        html_message = render_message(html_message, context)

        email = EmailModel(
            from_email=sender,
            subject=subject,
            message=message,
            html_message=html_message,
            scheduled_time=scheduled_time,
            expires_at=expires_at,
            message_id=message_id,
            headers=headers,
            priority=priority,
            status=status,
            backend_alias=backend,
            template=template,
        )

        if commit:
            email.save()
            set_recipients(email, recipients_addresses, cc_addresses, bcc_addresses)

    return email


def send(
        recipients=None,
        sender=None,
        template=None,
        context=None,
        subject='',
        message='',
        html_message='',
        scheduled_time=None,
        expires_at=None,
        headers=None,
        priority=None,
        attachments=None,
        render_on_delivery=False,
        log_level=None,
        commit=True,
        cc=None,
        bcc=None,
        language='',
        backend='',
):
    # if not language:
    #     language = get_default_language()
    # else:
    #     if language not in get_languages_list():
    #         raise ValidationError(f'Language "{language}" is not found in LANGUAGES configuration.')
    try:
        recipients = parse_emails(recipients)
    except ValidationError as e:
        raise ValidationError('recipients: %s' % e.message)

    try:
        cc = parse_emails(cc)
    except ValidationError as e:
        raise ValidationError('c: %s' % e.message)

    try:
        bcc = parse_emails(bcc)
    except ValidationError as e:
        raise ValidationError('bcc: %s' % e.message)

    if sender is None:
        sender = settings.DEFAULT_FROM_EMAIL

    priority = parse_priority(priority)

    if log_level is None:
        log_level = get_log_level()

    if not commit:
        if priority == PRIORITY.now:
            raise ValueError("send_many() can't be used with priority = 'now'")
        if attachments:
            raise ValueError("Can't add attachments with send_many()")

    if template:
        if subject:
            raise ValueError('You can\'t specify both "template" and "subject" arguments')
        if message:
            raise ValueError('You can\'t specify both "template" and "message" arguments')
        if html_message:
            raise ValueError('You can\'t specify both "template" and "html_message" arguments')

        # template can be an EmailTemplate instance or name
        if isinstance(template, EmailMergeModel):
            template = template
            # If language is specified, ensure template uses the right language
            if language and template.language != language:
                template = template.translated_templates.get(language=language)
        else:
            template = get_email_template(template, language)

    if backend and backend not in get_available_backends().keys():
        raise ValueError('%s is not a valid backend alias' % backend)

    email = create(
        sender,
        recipients,
        cc,
        bcc,
        subject,
        message,
        html_message,
        context,
        scheduled_time,
        expires_at,
        headers,
        template,
        priority,
        render_on_delivery,
        commit=commit,
        backend=backend,
        language=language or template.language
    )

    if attachments:
        attachments = create_attachments(attachments)
        email.attachments.add(*attachments)

    if priority == PRIORITY.now:
        email.dispatch(log_level=log_level)
    elif commit:
        email_queued.send(sender=EmailModel, emails=[email])

    return email


def send_many(**kwargs):
    """
    This function allows to send multiple emails separately. Using it is beneficial if you need a user data as a
    context and you want to serve every recipient separately.
    """
    if not (recipients := parse_emails(kwargs.pop('recipients'))):
        raise ValueError('You must specify recipients')

    recipients_objs = get_recipients_objects(recipients)

    context = kwargs.pop('context', {})
    emails = [send(recipients=[recipient.email], context={**context, 'recipient': recipient}, commit=False, **kwargs)
              for recipient in recipients_objs]

    if emails:

        emails = EmailModel.objects.bulk_create(emails)

        email_recipients = []
        for email, recipient in list(zip(emails, recipients_objs)):
            email_recipients.append(Recipient(email=email, address=recipient, send_type='to'))
        Recipient.objects.bulk_create(email_recipients)

        email_queued.send(sender=EmailModel, emails=emails)


def get_queued():
    """
    Returns the queryset of emails eligible for sending – fulfilling these conditions:
     - Status is queued or requeued
     - Has scheduled_time before the current time or is None
     - Has expires_at after the current time or is None
    """
    now = timezone.now()
    query = (Q(scheduled_time__lte=now) | Q(scheduled_time=None)) & (Q(expires_at__gt=now) | Q(expires_at=None))
    return (
        EmailModel.objects.filter(query, status__in=[STATUS.queued, STATUS.requeued])
        .select_related('template')
        .order_by(*get_sending_order())
        .prefetch_related('attachments')[: get_batch_size()]
    )


def send_queued(processes=1, log_level=None):
    """
    Sends out all queued mails that has scheduled_time less than now or None
    """
    queued_emails = get_queued()
    total_sent, total_failed, total_requeued = 0, 0, 0
    total_email = len(queued_emails)

    logger.info('Started sending %s emails with %s processes.' % (total_email, processes))

    if log_level is None:
        log_level = get_log_level()

    if queued_emails:
        # Don't use more processes than number of emails
        if total_email < processes:
            processes = total_email

        if processes == 1:
            total_sent, total_failed, total_requeued = _send_bulk(
                emails=queued_emails,
                uses_multiprocessing=False,
                log_level=log_level,
            )
        else:
            email_lists = split_emails(queued_emails, processes)

            pool = Pool(processes)

            tasks = []
            for email_list in email_lists:
                tasks.append(pool.apply_async(_send_bulk, args=(email_list,)))

            timeout = get_batch_delivery_timeout()
            results = []

            # Wait for all tasks to complete with a timeout
            # The get method is used with a timeout to wait for each result
            for task in tasks:
                results.append(task.get(timeout=timeout))
            # for task in tasks:
            #     try:
            #         # Wait for all tasks to complete with a timeout
            #         # The get method is used with a timeout to wait for each result
            #         results.append(task.get(timeout=timeout))
            #     except (TimeoutError, ContextTimeoutError):
            #         logger.exception("Process timed out after %d seconds" % timeout)

            # results = pool.map(_send_bulk, email_lists)
            pool.terminate()
            pool.join()

            total_sent = sum(result[0] for result in results)
            total_failed = sum(result[1] for result in results)
            total_requeued = [result[2] for result in results]

    logger.info(
        '%s emails attempted, %s sent, %s failed, %s requeued',
        total_email,
        total_sent,
        total_failed,
        total_requeued,
    )

    return total_sent, total_failed, total_requeued


def _send_bulk(emails, uses_multiprocessing=True, log_level=None):
    # Multiprocessing does not play well with database connection
    # Fix: Close connections on forking process
    # https://groups.google.com/forum/#!topic/django-users/eCAIY9DAfG0
    if uses_multiprocessing:
        db_connection.close()

    if log_level is None:
        log_level = get_log_level()

    sent_emails = []
    failed_emails = []  # This is a list of two tuples (email, exception)
    email_count = len(emails)

    logger.info('Process started, sending %s emails' % email_count)

    def send(email):
        try:
            email.dispatch(log_level=log_level, commit=False, disconnect_after_delivery=False)
            sent_emails.append(email)
            logger.debug('Successfully sent email #%d' % email.id)
        except Exception as e:
            logger.exception('Failed to send email #%d' % email.id)
            failed_emails.append((email, e))

    # Prepare emails before we send these to threads for sending
    # So we don't need to access the DB from within threads
    for email in emails:
        # Sometimes this can fail, for example when trying to render
        # email from a faulty Django template
        try:
            email.prepare_email_message()
        except Exception as e:
            logger.exception('Failed to prepare email #%d' % email.id)
            failed_emails.append((email, e))

    # number_of_threads = min(get_threads_per_process(), email_count)
    # pool = ThreadPool(number_of_threads)

    # results = []
    for email in emails:
        send(email)

    # timeout = get_batch_delivery_timeout()

    # Wait for all tasks to complete with a timeout
    # The get method is used with a timeout to wait for each result
    # for result in results:
    #     result.get(timeout=timeout)
    # for result in results:
    #     try:
    #         # Wait for all tasks to complete with a timeout
    #         # The get method is used with a timeout to wait for each result
    #         result.get(timeout=timeout)
    #     except TimeoutError:
    #         logger.exception("Process timed out after %d seconds" % timeout)

    # pool.close()
    # pool.join()

    connections.close()

    # Update statuses of sent emails
    email_ids = [email.id for email in sent_emails]
    EmailModel.objects.filter(id__in=email_ids).update(status=STATUS.sent)

    # Update statuses and conditionally requeue failed emails
    num_failed, num_requeued = 0, 0
    max_retries = get_max_retries()
    scheduled_time = timezone.now() + get_retry_timedelta()
    emails_failed = [email for email, _ in failed_emails]

    for email in emails_failed:
        if email.number_of_retries is None:
            email.number_of_retries = 0
        if email.number_of_retries < max_retries:
            email.number_of_retries += 1
            email.status = STATUS.requeued
            email.scheduled_time = scheduled_time
            num_requeued += 1
        else:
            email.status = STATUS.failed
            num_failed += 1

    EmailModel.objects.bulk_update(emails_failed, ['status', 'scheduled_time', 'number_of_retries'])

    # If log level is 0, log nothing, 1 logs only sending failures
    # and 2 means log both successes and failures
    if log_level >= 1:
        logs = []
        for email, exception in failed_emails:
            logs.append(
                Log(
                    email=email,
                    status=STATUS.failed,
                    message=str(exception),
                    exception_type=type(exception).__name__,
                )
            )

        if logs:
            Log.objects.bulk_create(logs)

    if log_level == 2:
        logs = []
        for email in sent_emails:
            logs.append(Log(email=email, status=STATUS.sent))

        if logs:
            Log.objects.bulk_create(logs)

    logger.info(
        'Process finished, %s attempted, %s sent, %s failed, %s requeued',
        email_count,
        len(sent_emails),
        num_failed,
        num_requeued,
    )

    return len(sent_emails), num_failed, num_requeued


def send_queued_mail_until_done(processes=1, log_level=None):
    """
    Send mail in queue batch by batch, until all emails have been processed.
    """
    try:
        with db_lock('send_queued_mail_until_done'):
            logger.info('Acquired lock for sending queued emails')
            while True:
                try:
                    send_queued(processes, log_level)
                except Exception as e:
                    logger.exception(e, extra={'status_code': 500})
                    raise

                # Close DB connection to avoid multiprocessing errors
                db_connection.close()

                if not get_queued().exists():
                    break
    except TimeoutException:
        logger.info('Sending queued mail required too long, terminating now.')
    except LockedException:
        logger.info('Failed to acquire lock, terminating now.')
