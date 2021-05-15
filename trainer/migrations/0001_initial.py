# Generated by Django 2.2 on 2021-05-15 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DomainPrefix',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain_prefix', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FQDN',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fqdn', models.CharField(max_length=1000)),
                ('fqdn_type', models.CharField(choices=[('m', 'Malicious'), ('b', 'Benign'), ('u', 'Unknown')], default='u', max_length=25)),
                ('for_training', models.BooleanField(default=False, verbose_name='Use For Training')),
            ],
        ),
        migrations.CreateModel(
            name='FQDNInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fqdn_full', models.CharField(max_length=512, null=True)),
                ('fqdn_tested', models.CharField(max_length=512, null=True)),
                ('fqdn_type', models.CharField(max_length=25, null=True)),
                ('score', models.FloatField(default=0.0, null=True)),
                ('model_match', models.CharField(max_length=128, null=True)),
                ('fqdn_subdomain', models.CharField(max_length=200, null=True)),
                ('fqdn_domain', models.CharField(max_length=200, null=True)),
                ('entropy', models.FloatField(default=0.0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(default=False, max_length=128)),
                ('model_version', models.FloatField(default=1.0, null=True)),
                ('model_description', models.TextField(default='', max_length=256, null=True)),
                ('model_algorithm', models.CharField(default=False, max_length=128, null=True)),
                ('model_creation_date', models.DateTimeField(null=True)),
                ('model_malicious_count', models.IntegerField(default=0, null=True)),
                ('model_benign_count', models.IntegerField(default=0, null=True)),
                ('accuracy_training_set', models.FloatField(default=0.0, null=True)),
                ('accuracy_test_set', models.FloatField(default=0.0, null=True)),
                ('accuracy_precision', models.FloatField(default=0.0, null=True)),
                ('accuracy_recall', models.FloatField(default=0.0, null=True)),
                ('model_running', models.BooleanField(default=False, null=True)),
                ('model_binary', models.BinaryField(null=True)),
                ('model_attributes', models.BinaryField(null=True)),
                ('set_as_default', models.BooleanField(default=False, null=True)),
            ],
        ),
    ]
