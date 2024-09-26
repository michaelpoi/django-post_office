from datetime import timedelta

import pytest
from post_office.mail import create, send, send_many, split_into_batches, get_queued, _send_bulk
from post_office.models import PRIORITY, EmailModel, EmailAddress, EmailMergeModel, PlaceholderContent, STATUS, \
    Attachment, Recipient
from django.core.exceptions import ValidationError
import tempfile
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.utils import timezone
from django.conf import settings


@pytest.fixture
def template():
    common = {
        'base_file': 'email/default.html',
        'name': 'test_template',
        'description': 'test_description'
    }
    temp = EmailMergeModel.objects.create(
        **common,
        subject='template_subject',
        content='template_content',
        language='en',
        default_template=None,
    )
    trans_temp = EmailMergeModel.objects.create(
        **common,
        subject='de_template_subject',
        content='de_template_content',
        language='de',
        default_template=temp
    )
    common = {'emailmerge': temp,
              'base_file': 'email/test.html'}

    kwargs_en = [
        {'placeholder_name': 'test1',
         'content': 'test_content1', },
        {'placeholder_name': 'test2',
         'content': 'test_content2', },
    ]

    kwargs_de = [
        {'placeholder_name': 'test1',
         'content': 'de_test_content1', },
        {'placeholder_name': 'test2',
         'content': 'de_test_content2', },
    ]

    placeholders_en = [PlaceholderContent.objects.create(**{**kwarg, "language": 'en', **common}) for kwarg in
                       kwargs_en]
    placeholders_de = [PlaceholderContent.objects.create(**{**kwarg, "language": 'de', **common}) for kwarg in
                       kwargs_de]

    return temp


@pytest.fixture
def recipient():
    return EmailAddress.objects.create(email='john@gmail.com',
                                       first_name='John',
                                       last_name='Doe',
                                       gender='male',
                                       preferred_language='en')


@pytest.mark.django_db
def test_create_email(template):
    recipients = ['rec1@gmail.com', 'rec2@gmail.com']
    sender = 'sender@gmail.com'

    email_model = create(sender=sender,
                         recipients=recipients,
                         subject='subject',
                         message='message',
                         html_message='html_message',
                         priority='medium',
                         commit=True)

    assert EmailModel.objects.count() == 1
    email = EmailModel.objects.first()
    assert email.id == email_model.id
    assert email.from_email == sender
    assert email.subject == 'subject'
    assert email.message == 'message'
    assert email.html_message == 'html_message'
    assert email.priority == PRIORITY.medium
    assert (recipient_id := email.context['recipient'])
    assert email.status == STATUS.queued
    assert EmailAddress.objects.count() == 2

    assert EmailAddress.objects.get(pk=recipient_id).email == recipients[0]

    create(sender=sender,
           recipients=recipients,
           subject='subject',
           message='message',
           html_message='html_message',
           priority='medium',
           commit=False)

    assert EmailModel.objects.count() == 1

    email_model = create(sender=sender,
                         recipients=recipients,
                         template=template,
                         priority='medium',
                         commit=True)

    assert EmailModel.objects.count() == 2
    email = EmailModel.objects.last()
    assert email.id == email_model.id
    assert email.subject == 'template_subject'
    assert email.message == 'template_content'

    new_recipient = EmailAddress.objects.create(email='john@gmail.com',
                                                first_name='John',
                                                last_name='Doe',
                                                gender='male',
                                                preferred_language='en')

    context = {'recipient': new_recipient}
    email_model = create(sender=sender,
                         recipients=recipients,
                         template=template,
                         priority='medium',
                         commit=True,
                         context=context)

    assert email_model.context['recipient'] == new_recipient.id

    cc = ['cc1@gmail.com', 'cc2@gmail.com']
    bcc = ['bcc1@gmail.com', 'bcc2@gmail.com']
    email_model = create(sender=sender,
                         cc=cc,
                         bcc=bcc,
                         template=template,
                         priority='medium',
                         commit=True,
                         context=context)
    em = EmailModel.objects.get(pk=email_model.id)
    assert em.recipients.count() == 4
    assert list(em.recipients.values_list('email', flat=True)).sort() == [*cc, *bcc].sort()


@pytest.mark.django_db
def test_send_email(template, recipient):
    recipients = ['rec1@gmail.com', 'rec2@gmail.com']
    cc = ['cc1@gmail.com', 'cc2@gmail.com']
    bcc = ['bcc1@gmail.com', 'bcc2@gmail.com']
    sender = 'sender@gmail.com'
    context = {'recipient': recipient}
    email_model = send(sender=sender,
                       recipients=recipients,
                       template=template,
                       priority='medium',
                       commit=True,
                       context=context,
                       cc=cc,
                       bcc=bcc)
    assert email_model.template.language == 'en'

    with pytest.raises(ValidationError):
        send(sender=sender,
             recipients=recipients,
             template=template,
             priority='medium',
             commit=True,
             context=context,
             language='es')

    with pytest.raises(ValidationError):
        nv_recipients = [*recipients, 'not_valid']
        send(sender=sender,
             recipients=nv_recipients,
             template=template,
             priority='medium',
             commit=True,
             context=context,
             language='en')

    with pytest.raises(ValidationError):
        nv_cc = [*cc, 'not_valid']
        send(sender=sender,
             recipients=recipients,
             template=template,
             priority='medium',
             commit=True,
             context=context,
             language='en',
             cc=nv_cc)

    with pytest.raises(ValidationError):
        nv_bcc = [*bcc, 'not_valid']
        send(sender=sender,
             recipients=recipients,
             template=template,
             priority='medium',
             commit=True,
             context=context,
             language='en',
             cc=cc,
             bcc=nv_bcc)

    mail = send(
        recipients=recipients,
        template=template,
        priority='medium',
        commit=True,
        context=context,
        language='en',
        cc=cc)

    assert mail.from_email == 'default@email.com'

    with pytest.raises(ValueError):
        send(
            recipients=recipients,
            template=template,
            priority='now',
            commit=False,
            context=context,
            language='en',
            cc=cc)

    with pytest.raises(ValueError):
        send(recipients=recipients,
             template=template,
             subject='subject',
             priority='medium',
             commit=True,
             context=context,
             language='en', )

    with pytest.raises(ValueError):
        send(recipients=recipients,
             template=template,
             message='message',
             priority='medium',
             commit=True,
             context=context,
             language='en', )

    with pytest.raises(ValueError):
        send(recipients=recipients,
             template=template,
             html_message='<h1>Hi</hi>',
             priority='medium',
             commit=True,
             context=context,
             language='en', )

    mail = send(
        recipients=recipients,
        template='test_template',
        priority='medium',
        commit=True,
        context=context,
        language='en',
    )

    assert mail.template == template

    assert EmailModel.objects.last().template == EmailMergeModel.objects.get(name='test_template', language='en')

    mail = send(
        recipients=recipients,
        template=template,
        priority='medium',
        commit=True,
        context=context,
        language='de',
    )

    assert mail.template == EmailMergeModel.objects.get(name='test_template', language='de')

    mail = send(
        recipients=recipients,
        template='test_template',
        priority='medium',
        commit=True,
        context=context,
        language='de',
    )

    assert mail.template == EmailMergeModel.objects.get(name='test_template', language='de')

    with pytest.raises(ValueError):
        send(
            recipients=recipients,
            template='test_template',
            priority='medium',
            commit=True,
            context=context,
            language='de',
            backend='nv_backend'
        )

    mail = send(
        recipients=recipients,
        template='test_template',
        priority='medium',
        commit=True,
        context=context,
        language='de',
        backend='default'
    )

    assert mail.backend_alias == 'default'

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b'Testing payload')
        tmp.seek(0)
        mail = send(
            recipients=recipients,
            template='test_template',
            priority='medium',
            commit=True,
            context=context,
            language='de',
            backend='default',
            attachments={'test.txt': tmp}
        )
    assert Attachment.objects.count() == 1
    attachment = Attachment.objects.first()
    assert list(mail.attachments.all()) == [attachment]

    mail = send(
        recipients=recipients,
        template='test_template',
        priority='now',
        commit=True,
        context=context,
        language='de',
        backend='default',
    )

    assert mail.status == STATUS.sent


@pytest.mark.django_db
def test_send_many(template):
    recipients = ['mrec1@gmail.com', 'mrec2@gmail.com']
    sender = 'from@gmail.com'
    with pytest.raises(ValueError):
        send_many(sender=sender, template=template)

    with pytest.raises(ValidationError):
        send_many(sender=sender, recipients=['nv', 'valid@email.com'], template=template)

    with CaptureQueriesContext(connection) as ctx:
        emails = send_many(
            sender=sender,
            template=template,
            recipients=recipients,
            context={'test': 'val'}
        )
        insert_queries = [query for query in ctx.captured_queries if query['sql'].strip().lower().startswith('insert')]

        # 1. Create EmailAddress in bulk_create
        # 2. Create Recipients in bulk_create
        # 3. Create EmailModels in bulk_create
        assert len(insert_queries) == 3

    assert len(emails) == 2
    assert EmailModel.objects.count() == 2

    mrec1 = EmailAddress.objects.get(email='mrec1@gmail.com')
    mrec2 = EmailAddress.objects.get(email='mrec2@gmail.com')

    assert list(emails[0].recipients.all()) == [mrec1]
    assert list(emails[1].recipients.all()) == [mrec2]

    rec_objs = Recipient.objects.all()
    assert rec_objs.count() == 2

    assert all([rec.send_type == 'to' for rec in rec_objs])
    assert [rec_objs[0].email, rec_objs[1].email] == emails

    assert emails[0].context == {'test': 'val', 'recipient': mrec1.id}
    assert emails[1].context == {'test': 'val', 'recipient': mrec2.id}

    new_recipients = ['nmrec1@gmail.com', 'nmrec2@gmail.com']

    with CaptureQueriesContext(connection) as ctx:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            with tempfile.NamedTemporaryFile(delete=False) as tmp2:
                tmp.write(b'Testing payload 1')
                tmp.seek(0)
                tmp2.write(b'Testing payload 2')
                tmp2.seek(0)
                emails = send_many(
                    sender=sender,
                    template=template,
                    recipients=new_recipients,
                    context={'test': 'val'},
                    attachments={'test.txt': tmp, 'new.txt': tmp2},
                )
        insert_queries = [query for query in ctx.captured_queries if
                          query['sql'].strip().lower().startswith('insert')]

        # 1. Create EmailAddress in bulk_create
        # 2. Create Recipients in bulk_create
        # 3. Create EmailModels in bulk_create
        # 4-5. Create Attachments (2 times)
        # 6. Create Through objects in bulk_create
        assert len(insert_queries) == 6

    assert emails[0].attachments.count() == 2

    assert list(emails[0].attachments.all()) == list(emails[1].attachments.all())

    assert list(emails[0].attachments.values_list('name', flat=True)) == ['test.txt', 'new.txt']


def test_split_batches(settings):
    settings.POST_OFFICE['BATCH_SIZE'] = 2
    assert split_into_batches([1, 2, 3, 4, 5, 6, 7]) == [[1, 2], [3, 4], [5, 6], [7]]


@pytest.mark.django_db
def test_get_queued():
    kwargs = {
        'from_email': 'bob@example.com',
        'subject': 'Test',
        'message': 'Message',
    }
    assert list(get_queued()) == []

    EmailModel.objects.create(status=STATUS.failed, **kwargs)
    EmailModel.objects.create(status=None, **kwargs)
    EmailModel.objects.create(status=STATUS.sent, **kwargs)
    assert list(get_queued()) == []

    queued_email = EmailModel.objects.create(status=STATUS.queued, scheduled_time=None, **kwargs)
    assert list(get_queued()) == [queued_email]

    scheduled_time = timezone.now() + timedelta(days=1)
    EmailModel.objects.create(status=STATUS.queued, scheduled_time=scheduled_time, **kwargs)
    assert list(get_queued()) == [queued_email]

    past_email = EmailModel.objects.create(
        status=STATUS.queued, scheduled_time=timezone.datetime(2010, 12, 13), **kwargs
    )
    assert list(get_queued()) == [queued_email, past_email]


from django.core import mail


@pytest.mark.django_db
def test_send_bulk(template):
    recipients = ['mrec1@gmail.com', 'mrec2@gmail.com']
    sender = 'from@gmail.com'
    context = {'test': 'val'}
    email = send(
        sender=sender,
        recipients=recipients,
        template=template,
        priority='medium',
        commit=True,
        context=context,
        language='de',
        backend='default',
    )
    _send_bulk([email], uses_multiprocessing=False)
    assert EmailModel.objects.get(id=email.id).status == STATUS.sent



