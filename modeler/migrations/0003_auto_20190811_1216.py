# Generated by Django 2.1.3 on 2019-08-11 17:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modeler', '0002_certstreamtask'),
    ]

    operations = [
        migrations.RenameField(
            model_name='certstreamtask',
            old_name='is_done',
            new_name='is_running',
        ),
    ]
