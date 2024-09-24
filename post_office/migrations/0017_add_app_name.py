from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('post_office', '0016_remove_emailmodel_bcc_remove_emailmodel_cc_and_more'), ]

    operations = [
        migrations.AlterModelOptions(
            name='Recipient',  # Replace with your model's name
            options={'app_label': 'post_office'},
        ),
    ]
