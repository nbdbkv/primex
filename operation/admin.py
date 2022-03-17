from django.contrib import admin
from django_2gis_maps.admin import DoubleGisAdmin
from nested_admin.nested import NestedModelAdmin, NestedStackedInline

from operation.models import (
    DeliveryStatus,
    ParcelOption,
    Parcel,
    Distance,
    DeliveryType,
    Packaging,
    PaymentDimension,
    Envelop,
    ParcelPayment,
    PaymentType,
    Payment,
    Direction,
    UserInfo,
    ParcelDimension,
    PaymentHistory
)


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
    list_display = ("sender", "code", "create_at",)
    #
    # def from_region (self, obj):
    #     parcel_payment = ParcelPayment.objects.get(parcel=obj)
    #     from_region = parcel_payment.delivery_type.distance.from_region.name
    #     return from_region
    #
    # def to_district(self, obj):
    #     parcel_payment = ParcelPayment.objects.get(parcel=obj)
    #     to_dictrict = parcel_payment.delivery_type.distance.to_district.name
    #     return to_dictrict

# class PaymentHistoryAdmin(admin.ModelAdmin):


admin.site.register(DeliveryStatus)
admin.site.register(ParcelOption)
admin.site.register(Parcel, ParcelAdmin)
admin.site.register(Distance)
admin.site.register(DeliveryType)
admin.site.register(Packaging)
admin.site.register(PaymentDimension)
admin.site.register(Envelop)
admin.site.register(PaymentType)
admin.site.register(PaymentHistory)
