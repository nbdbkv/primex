from rest_framework import serializers
from .models import (Parcel, Directions, Direction, ParcelInfo, DeliveryType,DeliveryDate, Envelope, Recipient, ParcelDate, UserInfo, Town, Area, Package)
from account.models import User

class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        #fields = ('pk', 'price', 'code', 'location_info', 'parcel_info', 'delivery_type', 'sender_info', 'package_type', 'create_at', 'delivery_date', 'recipient_info', 'sender', 'status' )
        fields = '__all__'

class TownSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Town
        fields = ('pk','name',)

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('pk','name',)

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

class PackageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

class EnvelopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envelope
        fields = '__all__'

class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = '__all__'

class ParcelDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelDate
        fields = ('pk','create_time',)

class DeliveryDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDate
        fields = ('pk','date',)
class SenderInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'phone',)

class ParcelStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('pk', 'status',)