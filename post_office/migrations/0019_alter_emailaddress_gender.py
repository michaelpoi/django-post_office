# Generated by Django 5.1 on 2024-09-09 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0018_emailaddress_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailaddress',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=15, null=True, verbose_name='Gender'),
        ),
    ]
