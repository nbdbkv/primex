from django.forms import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from operation.models import Parcel, Payment, PaymentType, PaymentHistory
from operation.choices import PaymentTypeChoices, PaymentHistoryType

import hashlib


class CashReceivingSerializer(serializers.Serializer):
    amount = serializers.DecimalField(required=True, max_digits=9, decimal_places=2)
    operation_id = serializers.CharField(required=True)
    parcel_code = serializers.SlugField(required=True)
    sha1_hash = serializers.CharField(required=True)

    def validate_parcel_code(self, parcel_code):
        try:
            Parcel.objects.get(code=parcel_code)
            return parcel_code
        except Parcel.DoesNotExist:
            raise ValidationError(message=_("Parcel does not exist"))

    def validate(self, attrs: dict) -> dict:
        sha1_hash = attrs.pop("sha1_hash")
        attrs["secret"] = settings.CASHBOX_SECRET

        data = [i[1] for i in sorted(attrs.items())]
        obj_str = "&".join(map(str, data))
        hash1 = hashlib.sha1(bytes(obj_str, "utf-8"))
        pbhash = hash1.hexdigest()
        if sha1_hash == pbhash:
            attrs["sha1_hash"] = sha1_hash
            return attrs
        raise ValidationError(message=_("Hash sums do not match"))


class BonusPaySerializer(serializers.Serializer):
    parcel_code = serializers.CharField()
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)

    def validate_parcel_code(self, parcel_code):
        try:
            self.parcel = Parcel.objects.get(code=parcel_code)
            return parcel_code
        except Parcel.DoesNotExist:
            raise ValidationError({"message": "Parcel does not exist"})

    def validate_amount(self, amount):
        self.user = self.context.get("request").user
        if self.user.points < amount:
            raise ValidationError({"message": "You do not have enought bonus"})
        return amount

    def get_payment_type(self):
        type = PaymentType.objects.get(type=PaymentTypeChoices.BONUS)
        return type

    def make_payment(self):
        data = self.validated_data
        if pay := Payment.objects.filter(
            parcel=self.parcel.payment, type=self.get_payment_type()
        ):
            pay = pay.first()
            pay.sum += data["amount"]
            pay.save()

            history = PaymentHistory.objects.get(parcel=self.parcel)
            history.sum += data["amount"]
            history.save()
        else:
            pay = Payment.objects.create(
                parcel=self.parcel.payment,
                type=self.get_payment_type(),
                sum=data["amount"],
            )

            PaymentHistory.objects.create(
                user=self.user,
                parcel=self.parcel,
                sum=pay.sum,
                payment_type=PaymentHistoryType.CREDIT,
                type=pay.type,
            )
        self.user.points -= data["amount"]
        self.user.save()
        cash_payment = self.parcel.payment.payment.get(
            type__type=PaymentTypeChoices.CASH
        )
        cash_payment.sum -= data["amount"]
        cash_payment.save()


class OPayPaymentSerializer(serializers.Serializer):
    requisite = serializers.CharField(required=True)
    serviceId = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)
    transactionId = serializers.IntegerField()

    def validate_requisite(self, requisite):
        try:
            self.parcel = Parcel.objects.get(code=requisite)
            return requisite
        except Parcel.DoesNotExist:
            raise ValidationError({"message": "Parcel does not exist"})
