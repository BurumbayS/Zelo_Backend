from django.db import models
from django.utils.timezone import localtime, now
# from django.contrib.postgres.fields.jsonb import JSONField
import os
from datetime import datetime, time, date, timedelta
from enum import Enum
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)

def get_image_path(instance, filename):
    return os.path.join('place_wallpapers', str(instance.id), filename)

# UserManager - это класс, определяющий методы create_user и createuperuser.
# Этот класс должен предшествовать классу AbstractBaseUser, который мы определили выше.
class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email,and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        try:
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user
        except:
            raise

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    """
    class UserRole(Enum):
        ADMIN    = "ADMIN"
        COURIER  = "COURIER"
        USER     = "USER"
        BUSINESS = "BUSINESS"

        @classmethod
        def choices(cls):
            return tuple((i.name, i.value) for i in cls)

    # USER = 'USER'
    # ADMIN = 'ADMIN'
    # COURIER = 'COURIER'
    # BUSINESS = 'BUSINESS'
    # USER_ROLES = (
    #     (USER,    'USER'),
    #     (ADMIN,   'ADMIN'),
    #     (COURIER, 'COURIER'),
    #     (BUSINESS,'BUSINESS')
    # )

    email = models.EmailField(max_length=40, unique=True)
    name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    phonenumber = models.CharField(max_length=12, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices(), blank=True, default="USER")
    address = models.JSONField(blank=True, null=True)
    place_id = models.ForeignKey('Place', on_delete = models.CASCADE, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self

class AuthToken(models.Model):
    user = models.ForeignKey('User', on_delete = models.CASCADE, primary_key = True)
    token = models.CharField(max_length = 1000, blank = False)

# Create your models here.
class Place(models.Model):
    name = models.CharField(max_length = 50, blank = False)
    description = models.CharField(max_length = 200, blank = True)
    address = models.CharField(max_length = 200, blank = False)
    latitude = models.FloatField(blank = False)
    longitude = models.FloatField(blank = False)
    delivery_min_price = models.IntegerField(default = 400)
    wallpaper = models.ImageField(upload_to='place_wallpapers/', blank = True, null = True)
    categories = models.JSONField(blank = True, null = True)
    not_working = models.BooleanField(default = False, verbose_name = "Не работает")
    is_active = models.BooleanField(default = False, verbose_name = "Активно")

class MenuItem(models.Model):
    name = models.CharField(max_length = 50, blank = False)
    description = models.CharField(max_length = 200, blank = False)
    price = models.IntegerField(default = 0)
    category = models.ForeignKey('MenuItemCategory',  on_delete = models.CASCADE, blank = True, null = True)
    place_id = models.ForeignKey('Place', on_delete = models.CASCADE)
    image = models.ImageField(upload_to = 'menu_item_image/', blank = True, null = True)
    stopped = models.BooleanField(default = False)

class MenuItemCategory(models.Model):
    name = models.CharField(max_length = 100, primary_key = True)

class Order(models.Model):
    place_id = models.ForeignKey('Place', on_delete = models.CASCADE)
    client_id = models.ForeignKey('User', on_delete = models.SET_NULL, blank=True, null=True)
    order_items = models.JSONField(default={})
    date = models.DateField(auto_now = False, null = True)
    time = models.TimeField(auto_now = False, null = True)
    status = models.CharField(max_length = 20)
    delivery_address = models.JSONField()
    delivery_price = models.IntegerField(default = 0)
    contact_phone = models.CharField(max_length = 20, default = "")
    comment = models.CharField(max_length = 500, blank = True, default = "")
    confirmed = models.BooleanField(default = False, verbose_name = "Подтвержден")
    canceled = models.BooleanField(default = False, verbose_name = "Отменен")

    def save(self, *args, **kwargs):
        if (self.date == None) & (self.time == None):
            self.date = datetime.date(localtime(now()))
            self.time = datetime.time(localtime(now()))
        super().save(*args, **kwargs)

class PushToken(models.Model):
    user_email = models.CharField(max_length=50, primary_key=True)
    token = models.CharField(max_length=1000, blank = False)
    user_id = models.CharField(max_length=1000, blank = False, default = "default")
    status = models.CharField(max_length=100, blank=True)
    place_id = models.IntegerField(blank=True, default=0, null=True)

class YandexMapGeocoderKey(models.Model):
    key = models.CharField(max_length = 1000)
