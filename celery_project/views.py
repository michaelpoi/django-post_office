from django.template import loader

from celery_project.tasks import sample
from django.http import HttpResponse
from post_office import mail
from post_office.models import EmailMergeModel, EmailAddress
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from post_office.utils import render_email_template


def index(request):
    try:
        mail.send(
            'poenko.mishany@gmail.com',
            'Mykhailo.Poienko@uibk.ac.at',
            html_message='<b>HI there</b>'
        )
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse('Success')


def send_template(request):


    # template.save()
    # template.recipients.set(EmailAddress.objects.all())

    mail.send(
        'poenko.mishany@gmail.com',
        'Mykhailo.Poienko@uibk.ac.at',
        template=EmailMergeModel.objects.get(name='test_1'),
        context={'name': 'Michael', 'surname': 'Poienko', 'age': 19}
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
