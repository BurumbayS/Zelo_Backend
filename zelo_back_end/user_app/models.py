from django.db import models
from django.utils.timezone import localtime, now
from django.contrib.postgres.fields.jsonb import JSONField
import os
from datetime import datetime, time, date, timedelta

def get_image_path(instance, filename):
    return os.path.join('place_wallpapers', str(instance.id), filename)

# Create your models here.
class Place(models.Model):
    name = models.CharField(max_length = 50, blank = False)
    description = models.CharField(max_length = 200, blank = True)
    address = models.CharField(max_length = 200, blank = False)
    latitude = models.FloatField(blank = False)
    longitute = models.FloatField(blank = False)
    delivery_min_price = models.IntegerField(default = 400)
    wallpaper = models.ImageField(upload_to='place_wallpapers/', blank=True, null=True)

class MenuItem(models.Model):
    name = models.CharField(max_length = 50, blank = False)
    description = models.CharField(max_length = 200, blank = False)
    price = models.IntegerField(default = 0)
    place_id = models.ForeignKey('Place', on_delete = models.CASCADE)
    image = models.ImageField(upload_to = 'menu_item_image/', blank = True, null = True)

class Order(models.Model):
    place_id = models.ForeignKey('Place', on_delete = models.CASCADE)
    date = models.DateField(auto_now = False, null = True)
    time = models.TimeField(auto_now = False, null = True)
    status = models.CharField(max_length = 20)
    delivery_address = JSONField()
    delivery_price = models.IntegerField(default = 0)
    contact_phone = models.CharField(max_length = 20, default = "")

    def save(self, *args, **kwargs):
        self.date = datetime.date(localtime(now()))
        self.time = datetime.time(localtime(now()))
        self.delivery_price = 999
        super().save(*args, **kwargs)
