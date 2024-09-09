# Generated by Django 5.1 on 2024-09-09 13:54

import post_office.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0022_alter_emailmergemodel_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailaddress',
            name='email',
            field=models.CharField(max_length=254, unique=True, validators=[post_office.validators.validate_email_with_name], verbose_name='Email From'),
        ),
        migrations.AlterField(
            model_name='emailmergemodel',
            name='extra_recipients',
            field=models.ManyToManyField(blank=True, help_text='extra bcc recipients', to='post_office.emailaddress'),
        ),
    ]
