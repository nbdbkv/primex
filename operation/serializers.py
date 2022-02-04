from rest_framework import serializers
from .models import (Parcel, Directions, Direction, ParcelInfo, DeliveryType, Envelope, Recipient, DeliveryDate, UserInfo)
from account.models import User

class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('pk', 'price', 'code', 'location_info', 'parcel_info', 'delivery_type', 'sender_info', 'envelope_type', 'create_at', 'delivery_date', 'recipient_info', 'sender', 'status' )
class ParcelPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('price',)

class ParcelPaymentWithBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('price',)

class DirectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Directions
        fields = '__all__'
class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = '__all__'

class ParametersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelInfo
        fields = '__all__'

class DeliveryTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryType
        fields = '__all__'

class EnvelopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envelope
        fields = '__all__'

class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = '__all__'

class DeliveryDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDate
        fields = ('pk','date',)

class SenderInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'phone',)