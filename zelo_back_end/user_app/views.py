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
    Order
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
def get_orders(request):
    try:
        orders = Order.objects.filter(place_id=1)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status = 404)
    if request.method == 'GET':
        serializer = OrderSerializer(orders, many = True)
        return JsonResponse(serializer.data, safe=False)

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

        order_jsonString = json.dumps(serializer.data)
        message = {
            'type': 'chat_message',
            'message': order_jsonString
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('ADMIN', message)
        async_to_sync(channel_layer.group_send)('PLACE_'+str(serializer.data['place_id']), message)

        response = {
            "code": 0,
            "success": True
        }
        return JsonResponse(response, safe = False)

# ----------------------------------------------------------------------- #
def sockets(request):
    return render(request, 'index.html')
