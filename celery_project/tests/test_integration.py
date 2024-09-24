from typing import List

import requests
import uuid
from post_office import mail
import pytest
from post_office.mail import _send_bulk
from django.conf import settings

from post_office.models import EmailModel


def cleanup_messages():
    requests.delete('http://127.0.0.1:8025/api/v1/messages/')


@pytest.mark.django_db
def test_message():
    cleanup_messages()
    emails: List[EmailModel] = []
    emails.append(mail.send(
        'poenko.mishany@gmail.com',
        'Mykhailo.Poienko@uibk.ac.at',
        subject='Letter #id#',
        context={'id': 1},
        html_message="Hi there",
        priority='now'
    ))
    data = requests.get('http://127.0.0.1:8025/api/v1/messages')
    data = data.json()
    raise Exception(data)
