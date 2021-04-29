# Generated by Django 2.1.3 on 2019-04-25 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0009_fqdninstance_fqdn_tested'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fqdninstance',
            name='brand_domain_match',
        ),
        migrations.RemoveField(
            model_name='fqdninstance',
            name='brand_subdomain_match',
        ),
        migrations.AddField(
            model_name='fqdninstance',
            name='brand_match',
            field=models.ManyToManyField(to='trainer.Brand'),
        ),
    ]
