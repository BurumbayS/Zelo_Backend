from django.urls import path, include
from user_app import views


urlpatterns = [
    path('places/', views.places),
    path('menuItems/<int:placeID>/', views.menuItems),
    path('order/', views.newOrder),
    path('sockets/', views.sockets),
    path('register/', views.UserAuth.as_view()),
]
