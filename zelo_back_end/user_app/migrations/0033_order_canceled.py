# Generated by Django 3.1.1 on 2020-12-27 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0032_place_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='canceled',
            field=models.BooleanField(default=False, verbose_name='Отменен'),
        ),
    ]
