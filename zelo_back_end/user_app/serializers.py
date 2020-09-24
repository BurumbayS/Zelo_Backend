from rest_framework import serializers
from django.utils.timezone import localtime, now
from datetime import datetime, time, date, timedelta

from .models import(
    Place,
    MenuItem,
    Order,
    User
)

class UserSerializer(serializers.ModelSerializer):

    date_joined = serializers.ReadOnlyField()

    class Meta(object):
        model = User
        fields = ('id', 'email', 'name', 'address','phonenumber', 'role',
                  'date_joined', 'password')
        extra_kwargs = {'password': {'write_only': True}}

class PlaceSerializer(serializers.ModelSerializer):
  class Meta:
    model = Place
    fields = "__all__"

class MenuItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = MenuItem
    fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
      model = Order
      fields = "__all__"
