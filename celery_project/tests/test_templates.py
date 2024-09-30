import pytest
from post_office.models import EmailMergeModel, PlaceholderContent, EmailAddress


@pytest.fixture
def test_template():
    template = EmailMergeModel.objects.create(
        base_file='test/test.html',
        name='test_name',
        description='test_description',
        subject='test_subject',
        content='test_content',
        language='en',
    )
    return template


@pytest.mark.django_db
def test_creation(test_template):
    assert EmailMergeModel.objects.count() == 2

    main = EmailMergeModel.objects.get(language='en')

    assert main.name == 'test_name'
    assert main.subject == 'test_subject'
    assert main.content == 'test_content'
    assert not main.default_template

    translated = EmailMergeModel.objects.get(language='de')

    assert translated.name == 'test_name'

    assert translated.subject == 'Subject, language: de'

    assert translated.content == 'Content, language: de'

    assert translated.default_template == main

    placeholders_base = PlaceholderContent.objects.values_list('base_file', flat=True)

    assert len(placeholders_base) == 4

    assert all([place == 'test/test.html' for place in placeholders_base])

    placeholders = PlaceholderContent.objects.values_list('placeholder_name', 'language')

    assert sorted(placeholders) == sorted([('test1', 'en'), ('test2', 'en'), ('test1', 'de'), ('test2', 'de')])

    assert PlaceholderContent.objects.get(placeholder_name='test1', language='en').content == ('Placeholder: test1, '
                                                                                               'Language: en')


@pytest.mark.django_db
def test_render_template(test_template):
    rendered = test_template.render_email_template()
    clean = rendered.replace('\n', '').replace('\t', '').replace('\r', '').strip()
    html_string = (' {% load post_office %}'
                   ' <!DOCTYPE html><html lang="en">'
                   '<head>'
                   '    <meta charset="UTF-8">'
                   '    <title>Test</title>'
                   '</head>'
                   '<body>'
                   '    Placeholder: test1, Language: en'
                   '    Placeholder: test2, Language: en'
                   '</body>'
                   '</html>').strip()
    assert clean == html_string

    template_context = EmailMergeModel.objects.create(
        base_file='test/context_test.html',
        name='test_name',
        description='test_description',
        subject='test_subject',
        content='test_content',
        language='en',
    )
    rendered = template_context.render_email_template(context_dict={'test_var': 'VALUE'},
                                                      recipient=EmailAddress.objects.create(
                                                          email='test@email.com',
                                                          first_name='Name',
                                                          last_name='Surname',
                                                      ))
    clean = rendered.replace('\n', '').replace('\t', '').replace('\r', '').strip()

    html_string = (' {% load post_office %}'
                   ' <!DOCTYPE html><html lang="en">'
                   '<head>'
                   '    <meta charset="UTF-8">'
                   '    <title>Test</title>'
                   '</head>'
                   '<body>'
                   '    Name'
                   '    Surname'
                   '    Placeholder: test1, Language: en'
                   '    Placeholder: test2, Language: en'
                   '    VALUE'
                   '</body>'
                   '</html>').strip()

    assert clean == html_string
