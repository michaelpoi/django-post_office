# Generated by Django 5.1 on 2024-09-09 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0023_alter_emailaddress_email_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EmailContent',
            new_name='PlaceholderContent',
        ),
    ]
