# Generated by Django 5.1 on 2024-09-09 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0019_alter_emailaddress_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailcontent',
            name='language',
            field=models.CharField(blank=True, default='', max_length=12),
        ),
    ]
