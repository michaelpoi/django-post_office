# Generated by Django 5.1 on 2024-10-10 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0002_emailmergecontentmodel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placeholdercontent',
            name='language',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('de', 'German')], default='', max_length=12),
        ),
    ]
