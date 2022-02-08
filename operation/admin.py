from django.contrib import admin
from django_2gis_maps.admin import DoubleGisAdmin
from nested_admin.nested import NestedModelAdmin, NestedStackedInline

from operation.models import (
    UserInfo,
    ParcelDimension,
    ParcelOptions,
    Direction,
    ParcelInfo,
    DeliveryType,
    Packaging,
    PayStatus,
    PaymentType,
    Payment,
    ParcelEnvelop,
    PaymentDimension,
    DimensionPrice,
    PriceList,
    ParcelPayment,
    DeliveryStatus,
    Parcel
)


class UserInfoInline(NestedStackedInline):
    model = UserInfo
    extra = 1


class ParcelDimensionInline(NestedStackedInline):
    model = ParcelDimension
    extra = 1


class DirectionInline(NestedStackedInline):
    model = Direction
    extra = 1
    multiple_markers = False


class ParcelInfoInline(NestedStackedInline):
    model = ParcelInfo
    extra = 1
    inlines = [UserInfoInline, ParcelDimensionInline, DirectionInline]


class PaymentInline(NestedStackedInline):
    model = Payment
    extra = 1


class ParcelPaymentInline(NestedStackedInline):
    model = ParcelPayment
    extra = 1
    inlines = [PaymentInline]


class ParcelAdmin(NestedModelAdmin):
    inlines = [ParcelInfoInline, ParcelPaymentInline]


admin.site.register(Parcel, ParcelAdmin)
admin.site.register(ParcelOptions)
admin.site.register(DeliveryType)
admin.site.register(Packaging)
admin.site.register(PayStatus)
admin.site.register(PaymentType)
admin.site.register(ParcelEnvelop)
admin.site.register(PaymentDimension)
admin.site.register(DimensionPrice)
admin.site.register(PriceList)
admin.site.register(DeliveryStatus)
