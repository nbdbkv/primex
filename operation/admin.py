from django.contrib import admin
from django_2gis_maps.admin import DoubleGisAdmin
from nested_admin.nested import NestedModelAdmin, NestedStackedInline

from .choices import DirectionChoices
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
    list_display = ("sender", "code", "create_at", "from_district", "to_district",)

    def from_district(self, obj):
        from_dis = obj.direction.get(type=DirectionChoices.FROM).district.name
        return from_dis

    def to_district(self, obj):
        to_dis = obj.direction.get(type=DirectionChoices.TO).district.name
        return to_dis

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
