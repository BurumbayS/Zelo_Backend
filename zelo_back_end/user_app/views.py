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
    PushToken
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

            response = {
                "code": 0,
                "token": token.decode("utf-8"),
                "user" : serializedUser.data
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

        try:
            user_token = PushToken.objects.update_or_create(user_email=user.email, defaults={
                "token": push_token,
                "user_id": user_id,
                "status": user.role,
                "place_id": user.place_id
            })
        except Exception as e:
            print(e)
            return ErrorResponse.response(e)


        response = {
            "code": 0,
            "success": True
        }
        return JsonResponse(response, safe = False)

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
def getPlaceOrders(request, placeID):
    try:
        today = datetime.date(localtime(now()))
        placeOrders = Order.objects.filter(place_id = placeID, date = today)
    except Exception as error:
        print(error)
        return ErrorResponse.response(error)

    serializer = OrderSerializer(placeOrders, many=True)
    for order in serializer.data:
        order['client'] = getOrderClient(order)
        order['place'] = getOrderPlace(order)

    return JsonResponse(serializer.data, safe=False)

# Create your views here.
@csrf_exempt
@api_view(['GET'])
def places(request):
    if request.method == 'GET':
        places = Place.objects.all()
        serializer = PlaceSerializer(places, many=True)
        return JsonResponse(serializer.data, safe=False)

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
def getAllOrders(request):
    try:
        today = datetime.date(localtime(now()))
        orders = Order.objects.filter(date = today)
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

        order = Order.objects.filter(id=serializer.data['id'])
        order_serializer = OrderSerializer(order, many=True)

        order_serializer.data[0]['place'] = getOrderPlace(order_serializer.data[0])
        order_serializer.data[0]['client'] = getOrderClient(order_serializer.data[0])

        order_jsonString = json.dumps(order_serializer.data[0])
        data = {
            "order": order_jsonString
        }

        sendNotification(order_serializer.data[0]['place_id'], data)

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
            "success": True
        }
        return JsonResponse(response, safe = False)

# ----------------------------------------------------------------------- #
def sockets(request):
    return render(request, 'index.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def sendNotification(place_id, data):
    place = PushToken.objects.get(place_id=place_id)
    admin = PushToken.objects.get(status="ADMIN")

    # player_id = '8917ddcc-35fa-485e-9a17-ca11938b6f59'
    os_app_id = '5573dacb-c34f-40f9-a46d-cc427ec3f23c'
    os_apikey = 'YTNjMjI0ZDItMWNmOC00Mzg0LWE0YTYtZmUwNjU4ZTcyYWJh'
    #
    # Init the client
    client = OneSignalAppClient(app_id=os_app_id, app_api_key=os_apikey)

    # Creates a new notification
    notification = Notification(os_app_id, Notification.DEVICES_MODE)
    notification.contents = {'en': "Новый заказ"}
    notification.data = data
    notification.include_player_ids = [place.user_id, admin.user_id]  # Must be a list!

    try:
        # Sends it!
        result = client.create_notification(notification)
    except HTTPError as e:
        result = e.response.json()

    print(result)
