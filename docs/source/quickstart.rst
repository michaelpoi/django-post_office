Quickstart
=========================

Send a simple email is really easy:

.. code-block:: python

    from post_office import mail

    mail.send(
        'recipient@example.com', # List of email addresses or list of EmailAddress also accepted
        'from@example.com',
        subject='My email',
        message='Hi there!',
        html_message='Hi <strong>there</strong>!',
    )

If you want to use templates:

- Create ``email`` folder in ``post_office`` template engine ``BASE_DIR``
- In your email folder create html file like following:

.. code-block:: django

    {% load post_office %}

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">#var#
        <title>Example email template</title>
    </head>
    <body>
        Hello, {{ username }}
        {% placeholder 'main' %}
    </body>
    </html>

- Open your admin interface and create a new Email Template instance:
    - Enter name. This will be used as identifier for your template.
    - Select Base File as your created html and click "Save and continue editing".
    - You will be requested to enter values to the placeholders you entered in the template. (``main`` in the example).

        You can specify variables to be filled with the context.

         ** Syntax is `#var#`. **

        Example: This is a simple mail created by #generator#

    - If you have more than 1 language configured you will be requested to fill values for all languages in ``LANGUAGES``.
    - Save your instance.

- To send an email with the created template:

.. code-block:: python

    from post_office import mail

    mail.send(
        'recipient@example.com', # List of email addresses or list of EmailAddress also accepted
        'from@example.com',
        template='your-template-here', # Could be an EmailTemplate instance or name
        context={'generator': 'post_office',
        'username': 'michaelpoi',}, # Context is used to fill both {{ var }} in html and #var# in ckeditor.
        language='en' # If not specified settings.LANGUAGE_CODE is used
    )

The above command will put your email on the queue so you can use the command in
your webapp without slowing down the request/response cycle too much.
To actually send them out, run python manage.py send_queued_mail.
You can schedule this management command to run regularly via cron:

.. code-block::

    * * * * * (/usr/bin/python manage.py send_queued_mail >> send_mail.log 2>&1)
