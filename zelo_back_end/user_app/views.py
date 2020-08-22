from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import PlaceSerializer, MenuItemSerializer, OrderSerializer
from .models import Place, MenuItem
from django.conf import settings
from rest_framework.parsers import JSONParser

# Create your views here.
@csrf_exempt
def places(request):
    if request.method == 'GET':
        places = Place.objects.all()
        print(places[0].address);
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
def newOrder(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = OrderSerializer(data = data)

        if serializer.is_valid():
            serializer.save();
        else:
            print(serializer.errors)
            return JsonResponse(serializer.errors, safe = False)

        response = {
            "code": 0,
            "success": True
        }
        return JsonResponse(response, safe = False)
