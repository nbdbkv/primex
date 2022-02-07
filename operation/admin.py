from django.contrib import admin
from django_2gis_maps.admin import DoubleGisAdmin
from account.models import User
from .models import (
    Parcel,
    Town,
    Area,
    UserInfo,
    PaymentType,
    ParcelInfo,
    Recipient,
    ParcelStatus,
    DeliveryType,
    Envelope,
    Directions,
    Direction,
    Package,
    ParcelOption,
    )

admin.site.register(Package),
admin.site.register(ParcelOption),
admin.site.register(Town),
admin.site.register(Area),
admin.site.register(Parcel),
admin.site.register(UserInfo),
admin.site.register(Recipient),
admin.site.register(PaymentType),
admin.site.register(ParcelInfo),
admin.site.register(ParcelStatus),
admin.site.register(DeliveryType),
admin.site.register(Envelope),
admin.site.register(Directions),
admin.site.register(Direction),
