# Generated by Django 3.1.1 on 2020-09-24 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0003_auto_20200924_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='address',
            field=models.JSONField(blank=True, default={}),
        ),
    ]
