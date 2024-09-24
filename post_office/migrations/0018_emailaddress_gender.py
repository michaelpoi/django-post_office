# Generated by Django 5.1 on 2024-09-09 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0017_add_app_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailaddress',
            name='gender',
            field=models.CharField(blank=True, choices=[('m', 'Male'), ('f', 'Female'), ('o', 'Other')], max_length=15, null=True, verbose_name='Gender'),
        ),
    ]
