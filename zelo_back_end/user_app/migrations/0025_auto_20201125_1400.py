# Generated by Django 3.1.1 on 2020-11-25 08:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0024_auto_20201123_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
