# Current status

## Testing Workflow

Current testing app is a celery_project not testapp. To run app enable redis first

1. In admin panel create a template:
    - Specify name
    - Click save and continue 
    - Changing base file leads to refresh of placeholders form (entered values are still saved for each placeholder in any base file)
    - Placeholders forms are automatically created for each language in LANGUAGES (lang code can be seen in readonly field)
    - Subject and content forms for every language in LANGUAGES are created as well
    - Placeholders can be filled with text and variables. Variable format is #var#
    - Note that #recipient.first_name#, #recipient.last_name#, #recipient.gender# are available from default template and can be filled in EmailAddressAdmin

2. To send emails snippets from celery_project.views can be used. Simple gui is on / of server
 - mail.send() render email once and sends to all user list (cc and bcc can be provided)
    * context for vars can be provided in parameters
    * if template is provided language can be specified (should be one of LANGUAGES)
    * If no language is specified default is used
    * recipient context is provided from the first recipient in the list
    * if template comes with inlines specify inlines=True
 - send_many() generates a private message for each user. Is beneficial because less db queries.
   * recipient context is specified for every letter

## Working plan:
1. Refactor so that rendering is in worker
2. Parse images
3. Finish writing tests (currently only utils.py are translated to pytest with addition of testing current functions)
4. Remove extra code left from the original package