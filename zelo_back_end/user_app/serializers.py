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
    role = serializers.SerializerMethodField(source='get_role')
    date_joined = serializers.ReadOnlyField()

    class Meta(object):
        model = User
        fields = ('id', 'email', 'name', 'address','phonenumber', 'role',
                  'date_joined', 'password', 'place_id')
        extra_kwargs = {'password': {'write_only': True}}

    def get_role(self, obj):
        return obj.role

class PlaceSerializer(serializers.ModelSerializer):
  class Meta:
    model = Place
    fields = "__all__"

class MenuItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = MenuItem
    fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField(source='get_client')
    place = serializers.SerializerMethodField(source='get_place')

    class Meta:
      model = Order
      fields = ('order_items', 'date', 'time', 'status', 'delivery_address',
                'delivery_price', 'contact_phone', 'comment', 'client', 'place')

    def get_client(self, obj):
        user = User.objects.get(email = obj.client_id)
        serializer = UserSerializer(user)
        return serializer.data

    def get_place(self, obj):
        place = Place.objects.get(id = obj.place_id.id)
        serializer = PlaceSerializer(place)
        return serializer.data
