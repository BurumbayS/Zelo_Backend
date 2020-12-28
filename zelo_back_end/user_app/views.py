from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import PlaceSerializer, MenuItemSerializer, OrderSerializer, UserSerializer
from .models import (
    Place,
    MenuItem,
    User,
    Order,
    PushToken,
    YandexMapGeocoderKey
)
import json
from django.conf import settings
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework_jwt.utils import jwt_payload_handler
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.signals import user_logged_in
from .custom_models import ErrorResponse
import jwt
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from requests.exceptions import HTTPError
from onesignalclient.app_client import OneSignalAppClient
from onesignalclient.notification import Notification
from datetime import datetime, time, date, timedelta
from django.utils.timezone import localtime, now
import random


# ----------------Authorization---------------------

@method_decorator(csrf_exempt, name='dispatch')
class UserAuth(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)

        if serializer.is_valid():
            serializer.save()
            response = {
                'code': 0,
                'user': serializer.data
            }
            return JsonResponse(response, status=201)
        else:
            return JsonResponse({"error": serializer.errors})

@method_decorator(csrf_exempt, name='dispatch')
class Login(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        try:
            user = User.objects.get(email=email, password=password)
        except Exception as e:
            return ErrorResponse.response("Пользователь с такими данными не существует")

        try:
            payload = jwt_payload_handler(user)
            token = jwt.encode(payload, settings.SECRET_KEY)
            user_logged_in.send(sender=user.__class__,
                                request=request, user=user)
            serializedUser = UserSerializer(user, many=False)

            is_open = False
            if (user.place_id != None):
                is_open = user.place_id.not_working

            response = {
                "code": 0,
                "token": token.decode("utf-8"),
                "user" : serializedUser.data,
                "is_open": is_open
            }

            return JsonResponse(response, status=200)

        except Exception as e:
            print(e)
            return ErrorResponse.response("Проблемы с авторизацией")

@method_decorator(csrf_exempt, name='dispatch')
class ResetPassword(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        user = request.user

        old_password = request.data['old_password']
        new_password = request.data['new_password']

        if (user.password != old_password):
            return ErrorResponse.response("Неверный старый пароль")

        updated_data = {"email": user.email, "password": new_password}
        serializer = UserSerializer(user, data=updated_data)

        if serializer.is_valid():
            serializer.save()
            response = {
                "code": 0,
                "success": True
            }
            return JsonResponse(response, safe = False)

        return ErrorResponse.response("Не удалось поменять пароль. Попробуйте снова")

@method_decorator(csrf_exempt, name='dispatch')
class PushNotifications(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        push_token = request.data['push_token']
        user_id = request.data['user_id']
        place_id = None

        if (user.place_id != None):
            place_id = user.place_id.id

        try:
            user_token = PushToken.objects.update_or_create(user_email=user.email, defaults={
                "token": push_token,
                "user_id": user_id,
                "status": user.role,
                "place_id": place_id
            })
        except Exception as e:
            print(e)
            return ErrorResponse.response(e)


        response = {
            "code": 0,
            "success": True
        }
        return JsonResponse(response, safe = False)




# ---------------------Order's methods------------------------

@csrf_exempt
def updateOrderStatus(request):
    data = JSONParser().parse(request)
    id = data['id']

    order = Order.objects.get(id=id)
    order.status = data['status']

    try:
        order.save()
    except Exception as error:
        return ErrorResponse.response(error)

    response = {
        "code": 0,
        "success": True
    }
    return JsonResponse(response, safe = False)

@csrf_exempt
def confirmOrder(request, orderID):
    order = Order.objects.get(id=orderID)
    order.confirmed = True

    try:
        order.save()
    except Exception as error:
        return ErrorResponse.response(error)

    data = {
        "is_new": True,
        "is_canceled": False,
        "order_id": order.id
    }

    place = PushToken.objects.get(place_id = order.place_id.id)
    sendNotification(place.user_id, data)

    response = {
        "code": 0,
        "success": True
    }
    return JsonResponse(response, safe = False)

@csrf_exempt
def cancelOrder(request, orderID):
    order = Order.objects.get(id=orderID)
    order.canceled = True

    try:
        order.save()
    except Exception as error:
        return ErrorResponse.response(error)

    data = {
        "is_new": False,
        "is_canceled": True,
        "order_id": order.id
    }

    admin = PushToken.objects.get(status = "ADMIN")
    sendNotification(admin.user_id, data)

    response = {
        "code": 0,
        "success": True
    }
    return JsonResponse(response, safe = False)

@csrf_exempt
def getPlaceOrders(request, placeID):
    try:
        today = datetime.date(localtime(now()))
        placeOrders = Order.objects.filter(place_id = placeID, date = today, confirmed = True).order_by('-time')
    except Exception as error:
        print(error)
        return ErrorResponse.response(error)

    serializer = OrderSerializer(placeOrders, many=True)
    for order in serializer.data:
        order['client'] = getOrderClient(order)
        order['place'] = getOrderPlace(order)

    return JsonResponse(serializer.data, safe=False)

# @csrf_exempt
# def getPlaceAllOrders(request, placeID):
#     try:
#         placeOrders = Order.objects.filter(place_id = placeID, confirmed = True)
#     except Exception as error:
#         print(error)
#         return ErrorResponse.response(error)
#
#     serializer = OrderSerializer(placeOrders, many=True)
#     for order in serializer.data:
#         order['client'] = getOrderClient(order)
#         order['place'] = getOrderPlace(order)
#
#     return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def getAllOrders(request):
    try:
        today = datetime.date(localtime(now()))
        orders = Order.objects.filter(date = today).order_by('-time')
    except Exception as e:
        return JsonResponse({"error": str(e)}, status = 404)
    if request.method == 'GET':
        serializer = OrderSerializer(orders, many = True)
        for order in serializer.data:
            order['client'] = getOrderClient(order)
            order['place'] = getOrderPlace(order)

        return JsonResponse(serializer.data, safe=False)

def getOrderClient(order):
    user = User.objects.get(id = order['client_id'])
    serializer = UserSerializer(user)
    return serializer.data
def getOrderPlace(order):
    place = Place.objects.get(id = order['place_id'])
    serializer = PlaceSerializer(place)
    return serializer.data


@csrf_exempt
def newOrder(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = OrderSerializer(data = data)

        if serializer.is_valid():
            serializer.save();
        else:
            print(serializer.errors)
            return JsonResponse(serializer.errors, safe = False)

        data = {
            "order_id": serializer.data['id']
        }

        # admin = PushToken.objects.get(status = "ADMIN")
        # sendNotification(admin.user_id, data)

        # message = {
        #     'type': 'chat_message',
        #     'message': order_jsonString
        # }
        #
        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)('ADMIN', message)
        # async_to_sync(channel_layer.group_send)('PLACE_'+str(serializer.data['place_id']), message)

        response = {
            "code": 0,
            "success": True,
            "order": serializer.data
        }
        return JsonResponse(response, safe = False)

@csrf_exempt
def getOrder(request, orderID):
    order = Order.objects.filter(id = orderID)
    serializer = OrderSerializer(order, many = True)

    serializer.data[0]['client'] = getOrderClient(serializer.data[0])
    serializer.data[0]['place'] = getOrderPlace(serializer.data[0])

    response = {
        "code": 0,
        "success": True,
        "order": serializer.data[0]
    }

    return JsonResponse(response, safe = False)



# ---------------Place's methods----------------------

# Create your views here.
@csrf_exempt
@api_view(['GET'])
def places(request):
    if request.method == 'GET':
        places = Place.objects.filter(is_active = True).order_by('?')
        serializer = PlaceSerializer(places, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def startPlaceShift(request, placeID):
    try:
        place = Place.objects.get(id = placeID)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status = 404)

    place.not_working = False

    try:
        place.save()
    except Exception as error:
        return ErrorResponse.response(error)

    response = {
        "code": 0,
        "success": True
    }
    return JsonResponse(response, safe = False)

@csrf_exempt
def closePlaceShift(request, placeID):
    try:
        place = Place.objects.get(id = placeID)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status = 404)

    place.not_working = True

    try:
        place.save()
    except Exception as error:
        return ErrorResponse.response(error)

    response = {
        "code": 0,
        "success": True
    }
    return JsonResponse(response, safe = False)


@csrf_exempt
def menuItems(request, placeID):
    try:
        menuItems = MenuItem.objects.filter(place_id = placeID)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status = 404)
    if request.method == 'GET':
        serializer = MenuItemSerializer(menuItems, many = True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def addMenuItemToStopList(request, itemID):

    item = MenuItem.objects.get(id = itemID)
    item.stopped = True

    try:
        item.save()
    except Exception as error:
        return ErrorResponse.response(error)

    response = {
        "code": 0,
        "success": True
    }
    return JsonResponse(response, safe = False)

@csrf_exempt
def removeMenuItemFromStopList(request, itemID):
    item = MenuItem.objects.get(id = itemID)
    item.stopped = False

    try:
        item.save()
    except Exception as error:
        return ErrorResponse.response(error)

    response = {
        "code": 0,
        "success": True
    }
    return JsonResponse(response, safe = False)


# ----------------------------------------------------------------------- #
def sockets(request):
    return render(request, 'index.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def support(request):
    return render(request, 'support.html')

def getPlaceTotal(request, placeID, date):
    orders = Order.objects.filter(place_id = placeID, date = date)

    count = 0
    total = 0
    for order in orders:
        count += 1
        print(order.date)
        for item in order.order_items:
            total += item['price'] * item['count']

    response = {
        "total": total,
        "count": count,
    }
    return JsonResponse(response, safe = False)

def getTotalForDay(request, date):
    orders = Order.objects.filter(date = date)

    count = 0
    total = 0
    for order in orders:
        count += 1
        print(order.date)
        for item in order.order_items:
            total += item['price'] * item['count']

    response = {
        "total": total,
        "count": count,
    }
    return JsonResponse(response, safe = False)
# ---------------------------------------------

def sendNotification(user_id, data):
    # place = PushToken.objects.get(place_id = place_id)
    # admin = PushToken.objects.get(status = "ADMIN")

    # player_id = '8917ddcc-35fa-485e-9a17-ca11938b6f59'
    os_app_id = '5573dacb-c34f-40f9-a46d-cc427ec3f23c'
    os_apikey = 'YTNjMjI0ZDItMWNmOC00Mzg0LWE0YTYtZmUwNjU4ZTcyYWJh'
    #
    # Init the client
    client = OneSignalAppClient(app_id = os_app_id, app_api_key = os_apikey)

    # Creates a new notification
    notification = Notification(os_app_id, Notification.DEVICES_MODE)
    notification.contents = {'en': "Новый заказ"}
    notification.data = data
    notification.include_player_ids = [user_id]  # Must be a list!

    try:
        # Sends it!
        result = client.create_notification(notification)
    except HTTPError as e:
        result = e.response.json()

    print(result)

@csrf_exempt
def getMapApiKey(request):
    keys = YandexMapGeocoderKey.objects.all()

    response = {
        "code": 0,
        "success": True,
        "key": keys[0].key
    }

    return JsonResponse(response, safe=False)
