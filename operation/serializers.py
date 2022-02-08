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


class CreateParcelSerializer(serializers.Serializer):
    pass