# Generated by Django 3.1.1 on 2020-10-01 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0010_auto_20200929_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='place_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user_app.place'),
        ),
    ]
