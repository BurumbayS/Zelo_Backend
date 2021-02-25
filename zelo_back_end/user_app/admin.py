from django.contrib import admin
from .models import Place, MenuItem, Order, User, PushToken, MenuItemCategory, YandexMapGeocoderKey, AuthToken, Promocode, PromocodeType, UsedPromocode, DeliveryData

# Register your models here.
admin.site.register(Place)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(User)
admin.site.register(PushToken)
admin.site.register(MenuItemCategory)
admin.site.register(YandexMapGeocoderKey)
admin.site.register(AuthToken)
admin.site.register(Promocode)
admin.site.register(PromocodeType)
admin.site.register(UsedPromocode)
admin.site.register(DeliveryData)
