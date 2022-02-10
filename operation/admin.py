from django.contrib import admin
from django_2gis_maps.admin import DoubleGisAdmin
from nested_admin.nested import NestedModelAdmin, NestedStackedInline, NestedInlineModelAdmin

from operation.models import (
    DeliveryStatus,
    ParcelOption,
    Parcel,
    DeliveryType,
    Packaging,
    PayStatus,
    PriceList,
    Envelop,
    PriceEnvelop,
    PaymentDimension,
    DimensionPrice,
    ParcelPayment,
    PaymentType,
    Payment,
    Direction,
    UserInfo,
    ParcelDimension
)


class DimensionPriceInline(NestedStackedInline):
    model = DimensionPrice
    extra = 1


class PriceListAdmin(NestedModelAdmin):
    inlines = [DimensionPriceInline]


class PaymentInline(NestedStackedInline):
    model = Payment
    extra = 1


class ParcelPaymentInline(NestedStackedInline):
    model = ParcelPayment
    extra = 1
    inlines = [PaymentInline]


class DirectionInline(NestedStackedInline):
    model = Direction
    extra = 1


class UserInfoInline(NestedStackedInline):
    model = UserInfo
    extra = 1


class ParcelDimensionInline(NestedStackedInline):
    model = ParcelDimension
    extra = 1


class ParcelAdmin(NestedModelAdmin):
    inlines = [ParcelPaymentInline, DirectionInline, UserInfoInline, ParcelDimensionInline]


admin.site.register(Parcel, ParcelAdmin)
admin.site.register(PriceList, PriceListAdmin)
admin.site.register(DeliveryStatus)
admin.site.register(ParcelOption)
admin.site.register(DeliveryType)
admin.site.register(Packaging)
admin.site.register(PayStatus)
admin.site.register(Envelop)
admin.site.register(PriceEnvelop)
admin.site.register(PaymentDimension)
admin.site.register(PaymentType)
