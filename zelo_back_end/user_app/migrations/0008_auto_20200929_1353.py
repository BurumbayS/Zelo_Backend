# Generated by Django 3.1.1 on 2020-09-29 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0007_auto_20200925_0107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('ADMIN', 'ADMIN'), ('COURIER', 'COURIER'), ('USER', 'USER'), ('BUSINESS', 'BUSINESS')], max_length=20),
        ),
    ]
