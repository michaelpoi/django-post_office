import requests
import uuid
from post_office import mail
def cleanup_messages():
    requests.delete('http://127.0.0.1:8025/api/v1/messages/')

def test_message():
    cleanup_messages()
    test_subject = uuid.uuid4()
    mail.send(
        'poenko.mishany@gmail.com',
        'Mykhailo.Poienko@uibk.ac.at',
        subject=test_subject,
    )
    data = requests.get('http://127.0.0.1:8025/api/v1/messages')
    data = data.json()
    print(data)

