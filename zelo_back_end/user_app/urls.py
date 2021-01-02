from django.urls import path, include
from user_app import views


urlpatterns = [
    path('places/', views.places),
    path('menuItems/<int:placeID>/', views.menuItems),
    path('menuItems/<int:itemID>/addToStopList/', views.addMenuItemToStopList),
    path('menuItems/<int:itemID>/removeFromStopList/', views.removeMenuItemFromStopList),

    path('orders/', views.getAllOrders),
    path('order/', views.newOrder),
    path('update_order/', views.updateOrderStatus),
    path('<int:placeID>/orders/', views.getPlaceOrders),
    path('order/<int:orderID>/', views.getOrder),
    path('confirm_order/<int:orderID>/', views.confirmOrder),
    path('cancel_order/<int:orderID>/', views.cancelOrder),

    path('register/', views.UserAuth.as_view()),
    path('login/', views.Login.as_view()),
    path('reset_password/', views.ResetPassword.as_view()),

    path('sendPush/', views.sendNotification),
    path('push_token/', views.PushNotifications.as_view()),

    path('place/<int:placeID>/startShift/', views.startPlaceShift),
    path('place/<int:placeID>/closeShift/', views.closePlaceShift),

    path('allOrders/<int:placeID>/<str:date>/', views.getPlaceTotal),
    path('allOrders/<int:placeID>/<str:startDate>/<str:endDate>/', views.getPlaceTotalInRange),
    path('allOrders/<str:date>/', views.getTotalForDay),
    path('allOrders/<str:startDate>/<str:endDate>/', views.getTotalInRange),
    path('mapApiKey/', views.getMapApiKey),
    path('privacy_policy/', views.privacy_policy),
    path('support/', views.support),
    path('sockets/', views.sockets)
]
