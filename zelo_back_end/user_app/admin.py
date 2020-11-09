from django.contrib import admin
from .models import Place, MenuItem, Order, User, PushToken

# Register your models here.
admin.site.register(Place)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(User)
admin.site.register(PushToken)
