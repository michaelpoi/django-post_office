import pytest
from post_office.mail import create, send
from post_office.models import PRIORITY, EmailModel, EmailAddress, EmailMergeModel, PlaceholderContent, STATUS
from django.core.exceptions import ValidationError

@pytest.fixture
def template():
    temp = EmailMergeModel.objects.create(
        base_file='email/default.html',
        name='test_template',
        description='test_description',
        subject='template_subject',
        content='template_content',
        language='en',
        default_template=None,
    )
    common = {'emailmerge': temp,
              'language': 'en',
              'base_file': 'email/test.html'}

    kwargs = [
        {'placeholder_name': 'test1',
         'content': 'test_content1', },
        {'placeholder_name': 'test2',
         'content': 'test_content2', },
    ]

    placeholders = [PlaceholderContent.objects.create(**{**kwarg, **common}) for kwarg in kwargs]

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
    assert list(em.recipients.values_list('email', flat=True)) == [*cc, *bcc]


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

