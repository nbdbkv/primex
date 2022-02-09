from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from account.models import User
from operation.models import (
    UserInfo,
    ParcelDimension,
    Direction,
    DeliveryType,
    Packaging,
    PayStatus,
    PaymentType,
    Payment,
    PaymentDimension,
    DimensionPrice,
    PriceList,
    ParcelPayment,
    DeliveryStatus,
    Parcel
)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('info', 'phone',)

class CreateParcelSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    class Meta:
        model = Parcel
        fields = ('title',
                'description',
                'sender',
                'status',
                'code'
                'create_at',
                'option',
                'sending_date',)
        depth = 1

class ListParcelSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Parcel
        fields = ('title', 'description', 'sender', 'code', 'option', 'sending_date',)
        depth = 1
