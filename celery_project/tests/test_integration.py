import requests
import uuid
from post_office import mail
from post_office.mail import send_queued_mail_until_done
import pytest


def cleanup_messages():
    requests.delete('http://127.0.0.1:8025/api/v1/messages/')


@pytest.mark.django_db
def test_message():
    cleanup_messages()
    test_subject = str(uuid.uuid4())
    mail.send(
        'poenko.mishany@gmail.com',
        'Mykhailo.Poienko@uibk.ac.at',
        subject=test_subject,
    )
    send_queued_mail_until_done()
    data = requests.get('http://127.0.0.1:8025/api/v1/messages')
    data = data.json()
    print(data)
