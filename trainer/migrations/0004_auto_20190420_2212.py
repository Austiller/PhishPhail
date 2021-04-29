# Generated by Django 2.1.3 on 2019-04-21 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0003_auto_20190420_2211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='accuracty_test_set',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='model',
            name='accuracy_confusion_matrix',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='model',
            name='accuracy_training_set',
            field=models.FloatField(default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='model',
            name='confusion_matrix',
            field=models.FloatField(default=0.0, null=True),
        ),
    ]
