import logging
from django.core.files.base import ContentFile
import pytest
from post_office.utils import render_message, set_recipients, get_recipients_objects, parse_emails, parse_priority, \
    split_emails, create_attachments
from post_office.models import EmailAddress, EmailModel, PRIORITY, Attachment
from django.core.exceptions import ValidationError


def test_render_message():
    test_message = 'Test message'
    assert render_message(test_message, {}) == 'Test message'

    assert render_message('Test message#c#', {}) == 'Test message#c#'

    test_context = {
        'a': 10,
        'b': 20,
        'c': 'Hello',
        'disallowed_script': '<script>alert("Hello")</script>'
    }

    test_message_with_context = render_message('#c# I am #b#', test_context)

    assert test_message_with_context == 'Hello I am 20'

    assert render_message('#disallowed_script#', test_context) == ''

    assert render_message('##c##', test_context) == '#Hello#'

    test_recipient = EmailAddress(
        first_name='John',
        last_name='Doe',
        email='test@email.com',
        preferred_language='en',
        gender='male',
        is_blocked=False
    )

    test_message = '<p>Test message #recipient.first_name# #recipient.last_name#</p>'

    assert render_message(test_message, {'recipient': test_recipient}) == ('<p>Test message John '
                                                                           'Doe</p>')

    assert render_message(test_message, context={'recipient': test_recipient, 'recipient.first_name': 'Alisa'}) == (
        '<p>Test message Alisa Doe</p>')


@pytest.mark.django_db
def test_set_recipients():
    # Create test email
    test_email = EmailModel.objects.create(from_email='test@email.com')

    # Create test addresses
    to_recipients = [EmailAddress.objects.create(email=f"{i}@email.com") for i in range(5)]
    cc_recipients = [EmailAddress.objects.create(email=f"{i}@gmail.com") for i in range(5)]
    bcc_recipients = [EmailAddress.objects.create(email=f"{6 + i}@yahoo.com") for i in range(5)]

    # Test 'to' addresses
    set_recipients(test_email, to_addresses=to_recipients)

    assert test_email.recipients.count() == 5

    # Test 'cc' and 'bcc' addresses
    set_recipients(test_email, [], cc_addresses=cc_recipients, bcc_addresses=bcc_recipients)

    assert test_email.recipients.count() == 15

    # Validate recipients
    recipient_objs = test_email.recipients.through.objects.all()

    assert len(recipient_objs) == 15

    # Check 'to' recipients
    to_recipient_emails = [rec.address.email for rec in recipient_objs.filter(send_type='to')]
    assert sorted(to_recipient_emails) == sorted(addr.email for addr in to_recipients)

    # Check 'cc' recipients
    cc_recipient_emails = [rec.address.email for rec in recipient_objs.filter(send_type='cc')]
    assert sorted(cc_recipient_emails) == sorted(addr.email for addr in cc_recipients)

    # Check 'bcc' recipients
    bcc_recipient_emails = [rec.address.email for rec in recipient_objs.filter(send_type='bcc')]
    assert sorted(bcc_recipient_emails) == sorted(addr.email for addr in bcc_recipients)


@pytest.mark.django_db
def test_get_recipients(caplog):
    test_recipient = EmailAddress.objects.create(email='test1@email.com',
                                                 first_name='John',
                                                 last_name='Doe',
                                                 is_blocked=False)
    assert (recipient_list := get_recipients_objects(['test1@email.com'])) == [test_recipient]

    assert recipient_list[0].first_name, recipient_list[0].last_name == ('John', 'Doe')

    with caplog.at_level(logging.WARNING):
        new_recipients = get_recipients_objects(['test1@email.com', 'test2@email.com'])
        assert "is blocked" not in caplog.text

    created_recipient = EmailAddress.objects.get(email='test2@email.com')

    assert not created_recipient.is_blocked

    assert len(new_recipients) == 2
    assert new_recipients[1] == created_recipient

    test_recipient.is_blocked = True
    test_recipient.save()

    with caplog.at_level(logging.WARNING):
        recs = get_recipients_objects(['test1@email.com', 'test2@email.com'])
        assert "User test1@email.com is blocked and hence will be excluded" in caplog.text

    assert not created_recipient.is_blocked

    assert len(recs) == 1
    assert recs[0] == created_recipient


def test_parse_emails():
    assert parse_emails('test@exmaple.com') == ['test@exmaple.com']

    assert not parse_emails(None)

    with pytest.raises(ValidationError):
        parse_emails('invalid_email')

    with pytest.raises(ValidationError):
        parse_emails(['invalida_email', 'test@exmaple.com'])


def test_parse_priority():
    assert parse_priority('now') == PRIORITY.now
    assert parse_priority('high') == PRIORITY.high
    assert parse_priority('medium') == PRIORITY.medium
    assert parse_priority('low') == PRIORITY.low


@pytest.mark.django_db
def test_split_emails():
    for _ in range(225):
        EmailModel.objects.create(from_email='test@email.com')
    expected_size = [57, 56, 56, 56]
    email_list = split_emails(EmailModel.objects.all(), 4)
    assert expected_size == [len(emails) for emails in email_list]


@pytest.mark.django_db
def test_create_attachment():
    attachments = create_attachments(
        {
            'attachment_file1.txt': ContentFile('content'),
            'attachment_file2.txt': ContentFile('content'),
        }
    )

    assert len(attachments) == 2
    assert isinstance(attachments[0], Attachment)
    assert attachments[0].pk
    assert attachments[0].file.read() == b'content'
    assert attachments[0].name.startswith('attachment_file')
    assert attachments[0].mimetype == ''


@pytest.mark.django_db
def test_create_attachment_with_mimetype():
    attachments = create_attachments(
        {
            'attachment_file1.txt': {'file': ContentFile('content'), 'mimetype': 'text/plain'},
            'attachment_file2.jpg': {'file': ContentFile('content'), 'mimetype': 'text/plain'},
        }
    )

    assert len(attachments) == 2
    assert isinstance(attachments[0], Attachment)
    assert attachments[0].pk
    assert attachments[0].file.read() == b'content'
    assert attachments[0].name.startswith('attachment_file')
    assert attachments[0].mimetype == 'text/plain'


@pytest.mark.django_db
def test_create_attachments_open_file():
    attachments = create_attachments({'attachment_file.py': __file__})

    assert len(attachments) == 1
    assert isinstance(attachments[0], Attachment)
    assert attachments[0].pk
    assert attachments[0].file.read()
    assert attachments[0].name == 'attachment_file.py'
    assert attachments[0].mimetype == ''
