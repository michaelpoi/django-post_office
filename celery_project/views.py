from django.template import loader

from celery_project.tasks import sample
from django.http import HttpResponse
from post_office import mail
from post_office.models import EmailMergeModel, EmailAddress
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from post_office.utils import render_email_template


def index(request):
    mail.send(
        'poenko.mishany@gmail.com',
        'Mykhailo.Poienko@uibk.ac.at',
        html_message='This is a sample html to <p><strong>Hi</strong> Michael</p>. The idea is to demonstrate <p>How are you<strong> doing?</strong></p> Number of placeholders in <p>10</p> This will be writen by <p>Misha, Sasha, Test</p>'
    )
    return HttpResponse('Success')


def send_template(request):


    # template.save()
    # template.recipients.set(EmailAddress.objects.all())

    mail.send(
        ['poenko.mishany@gmail.com', 'test_recipient@gmail.com'],
        'Mykhailo.Poienko@uibk.ac.at',
        cc='cc@gmail.com',
        template=EmailMergeModel.objects.get(name='test_email'),
        context={'cont': 'Interesting', 'c': 10, 'name': 'Mishenka', 'pow': 'strenght'},
        render_on_delivery= True
    )
    return HttpResponse('Success')


def send_image(request):
    # EmailTemplate.objects.create(
    #     name='image_template',
    #     html_content="{% load post_office %} <p>... somewhere in the body ...</p><img src=\"{% inline_image "
    #                  "'images/welcome.jpg' %}\" />"
    # )
    template = get_template('image_template.html', using='post_office')
    subject, body = "Test Photo", "This mail contains test photo"
    from_email, to_email = 'poenko.mishany@gmail.com', 'Mykhailo.Poienko@uibk.ac.at',
    email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
    html = template.render()
    email_message.attach_alternative(html, 'text/html')
    template.attach_related(email_message)
    email_message.send()

    return HttpResponse('Success')


import tempfile


def send_attachment(request):
    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.write(b'Hello There')
        f.seek(0)
        mail.send(
            'poenko.mishany@gmail.com',
            'Mykhailo.Poienko@uibk.ac.at',
            html_message='<b>HI there</b>',
            attachments={'test.txt': f}
        )

    return HttpResponse('Success')


def test_new_system(request):
    temp = loader.get_template('email/placeholders.html')
    template = EmailMergeModel.objects.get(name='test_1')
    html_content = render_email_template(template)
    return HttpResponse(html_content)

def send_many(request):
    first_email = {
        'sender': 'from@example.com',
        'recipients': ['alice@example.com'],
        'subject': 'Hi!',
        'message': 'Hi Alice!'
    }
    second_email = {
        'sender': 'from@example.com',
        'recipients': ['bob@example.com'],
        'subject': 'Hi!',
        'message': 'Hi Bob!'
    }
    kwargs_list = [first_email, second_email]

    mail.send_many(kwargs_list)

    return HttpResponse('Sucess')
