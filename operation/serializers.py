from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

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


class CreateParcelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelInfo
        fields = '__all__'

class ListParcelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelInfo
        fields = '__all__'
        depth = 1
