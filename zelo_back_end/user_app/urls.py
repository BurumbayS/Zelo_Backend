from django.urls import path, include
from user_app import views


urlpatterns = [
    path('places/', views.places),
    path('menuItems/<int:placeID>/', views.menuItems),
    path('menuItems/<int:itemID>/addToStopList/', views.addMenuItemToStopList),
    path('menuItems/<int:itemID>/removeFromStopList/', views.removeMenuItemFromStopList),
    path('orders/', views.getAllOrders),
    path('order/', views.newOrder),
    path('sockets/', views.sockets),
    path('register/', views.UserAuth.as_view()),
    path('login/', views.Login.as_view()),
    path('reset_password/', views.ResetPassword.as_view()),
    path('sendPush/', views.sendNotification),
    path('push_token/', views.PushNotifications.as_view()),
    path('update_order/', views.updateOrderStatus),
    path('<int:placeID>/orders/', views.getPlaceOrders),
    path('order/<int:orderID>/', views.getOrder),
    path('confirm_order/<int:orderID>/', views.confirmOrder),

    path('mapApiKey/', views.getMapApiKey),
    path('privacy_policy/', views.privacy_policy),
    path('support/', views.support)
]
