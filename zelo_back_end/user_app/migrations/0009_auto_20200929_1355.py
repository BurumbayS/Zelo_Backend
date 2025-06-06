# Generated by Django 3.1.1 on 2020-09-29 07:55

from django.db import migrations, models
import user_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0008_auto_20200929_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('ADMIN', 'ADMIN'), ('COURIER', 'COURIER'), ('USER', 'USER'), ('BUSINESS', 'BUSINESS')], default=user_app.models.User.UserRole['USER'], max_length=20),
        ),
    ]
