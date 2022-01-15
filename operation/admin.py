from django.contrib import admin
from .models import *

admin.site.register(Parcel)
admin.site.register(UserInfo)
admin.site.register(PaymentType)
admin.site.register(DestinationType)
admin.site.register(ParcelOption)
admin.site.register(ParcelInfo)
admin.site.register(Direction)
admin.site.register(ParcelStatus)
admin.site.register(DeliveryType)