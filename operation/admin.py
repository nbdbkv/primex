from django.contrib import admin
from django.db.models import Sum
from nested_admin.nested import NestedModelAdmin, NestedStackedInline
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateTimeRangeFilter
from decimal import Decimal


from .choices import DirectionChoices, PaymentHistoryType, PaymentTypeChoices
from account.roles.mixins import ParcelAdminMixin
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
    PaymentHistory,
)
from .resource import ParcelResource


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


class ParcelAdmin(ImportExportModelAdmin, ParcelAdminMixin, NestedModelAdmin):
    resource_class = ParcelResource
    save_on_top = True
    inlines = [
        ParcelPaymentInline,
        DirectionInline,
        UserInfoInline,
        ParcelDimensionInline,
    ]
    change_form_template = "admin/print_receipt.html"
    list_display = (
        "sender",
        "code",
        "sending_date",
        "from_district",
        "to_district",
        "parcel_sum",
        "parcel_payment_types",
        "status",
    )
    search_fields = ["code", "sender__phone"]
    list_filter = [
        "status",
        "payment__payment__type__title",
        ("create_at", DateTimeRangeFilter),
    ]

    def save_model(self, request, obj, form, change):
        if change:
            parcel_payment = ParcelPayment.objects.get(id=obj.payment.id)
            if (
                parcel_payment.pay_status != obj.payment.pay_status
                and not PaymentHistory.objects.filter(
                    parcel=obj,
                    payment_type=PaymentHistoryType.DEBIT,
                    type__type=PaymentTypeChoices.BONUS,
                ).exists()
            ):
                bonus = float(obj.payment.price) * 0.05
                PaymentHistory.objects.create(
                    user=obj.sender,
                    parcel=obj,
                    type=PaymentType.objects.get(type=PaymentTypeChoices.BONUS),
                    sum=bonus,
                    payment_type=PaymentHistoryType.DEBIT,
                )
                obj.sender.points += Decimal(bonus)
                obj.sender.save()
        obj.save()

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return super().change_view(
            request, object_id, form_url="", extra_context={"obj_id": object_id}
        )

    @admin.display(description=_("payment type"))
    def parcel_payment_types(self, obj):
        types = obj.payment.payment.values_list("type__title", flat=True)
        return ", ".join(types)

    @admin.display(description=_("price"))
    def parcel_sum(self, obj):
        sum = obj.payment.payment.aggregate(Sum("sum"))["sum__sum"]
        return sum

    @admin.display(description=_("from district"))
    def from_district(self, obj):
        from_dis = obj.direction.get(type=DirectionChoices.FROM).district.name
        return from_dis

    @admin.display(description=_("to district"))
    def to_district(self, obj):
        to_dis = obj.direction.get(type=DirectionChoices.TO).district.name
        return to_dis


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
