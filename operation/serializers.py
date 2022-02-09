from django.forms import ValidationError
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from account.models import City, District
from account.validators import PhoneValidator
from operation.services import get_parcel_code
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


class PaymentSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'


class ParcelPaymentSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(many=True)
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ParcelPayment
        exclude = ('pay_status',)


class DirectionSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Direction
        fields = '__all__'
        

class UserInfoSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)
    phone = serializers.CharField(validators=[PhoneValidator])
    
    class Meta:
        model = UserInfo
        fields = '__all__'
        

class ParcelDimensionSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ParcelDimension
        fields = '__all__'


class CreateParcelSerializer(serializers.ModelSerializer):
    payment = ParcelPaymentSerializer()
    direction = DirectionSerializer(many=True)
    user_info = UserInfoSerializer(many=True)
    dimension = ParcelDimensionSerializer()
    
    class Meta:
        model = Parcel
        exclude = ('code', 'sender', 'create_at')
        
    def validate_direction(self, direction):
        if len(direction) != 2:
            raise ValidationError({'message': _('direction must be 2')})
        if direction[0].get('type') != 1:
            raise ValidationError({'message': 'wrong type'})
        if direction[1].get('type') != 2:
            raise ValidationError({'message': 'wrong type'})
        return direction
    
    @transaction.atomic
    def create(self, validated_data):
        payment = validated_data.pop('payment')
        direction = validated_data.pop('direction')
        user_info = validated_data.pop('user_info')
        dimension = validated_data.pop('dimension')
        
        validated_data['code'] = get_parcel_code(direction[1])
        validated_data['sender'] = self.context.get('request').user
        options = validated_data.pop('option')
        parcel = Parcel.objects.create(**validated_data)
        parcel.option.set(options)
        
        parcel_payments = payment.pop('payment')
        packaging = payment.pop('packaging')
        payment = ParcelPayment.objects.create(parcel_id=parcel.id, **payment)
        payment.packaging.set(packaging)
        for parcel_pay in parcel_payments:
            Payment.objects.create(parcel_id=payment.id, **parcel_pay)
        
        for dir in direction:
            Direction.objects.create(parcel_id=parcel.id, **dir)
        
        for user in user_info:
            UserInfo.objects.create(parcel_id=parcel.id, **user)
        
        dimension = ParcelDimension.objects.create(parcel_id=parcel.id, **dimension)
        return parcel
