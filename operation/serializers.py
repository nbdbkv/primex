from rest_framework import serializers
import drf_extra_fields
from .models import (Parcel, Directions, Direction, ParcelInfo, DeliveryType, Envelope, Recipient, ParcelDate, UserInfo, Town, Area, Package, ParcelOption)
from account.models import User

from drf_extra_fields.fields import Base64ImageField

class UploadedBase64ImageSerializer(serializers.Serializer):
    file = Base64ImageField()

class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('pk', 'price', 'code', 'location_info', 'parcel_info', 'delivery_type', 'sender_info', 'package_type', 'create_at', 'recipient_info', 'sender', 'status' )
        depth = 2
        #fields = '__all__'

class DirectionSerializer(serializers.ModelSerializer):
    pass

class TownSeralizer(serializers.ModelSerializer):
    direction = DirectionSerializer

    class Meta:
        model = Town
        fields = ('pk','name','directions',)

class AreaSerializer(serializers.ModelSerializer):
    directions = DirectionSerializer
    class Meta:
        model = Area
        fields = ('pk','name','directions',)


class ParcelPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('price',)

class ParcelPaymentWithBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('price',)

class DirectionsSerializer(serializers.ModelSerializer):
    location_info = ParcelSerializer

    class Meta:
        model = Directions
        fields = ('pk', 'from_location', 'to_location','location_info',)


class DirectionSerializer(serializers.ModelSerializer):
    directions = DirectionsSerializer
    class Meta:
        model = Direction
        depth = 2
        fields = "__all__"


class ParametersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelInfo
        fields = '__all__'

class DeliveryTypeSerializer(serializers.ModelSerializer):
    #image = UploadedBase64ImageSerializer()
    delivery_type = ParcelSerializer
    class Meta:
        model = DeliveryType
        fields = ('pk', 'name',)

class PackageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ('package_name',)

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

class SenderInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'info', 'phone',)

class ParcelStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('pk', 'status',)

class ParcelOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelOption
        fields = '__all__'


class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name','last_name', 'phone',)

class GetDirectionSerializer(serializers.ModelSerializer):
    area = AreaSerializer
    town = TownSeralizer
    class Meta:
        model = Direction
        fields = ('town', 'area','street', 'number',)

    def create(self, validated_data):
        return Direction.objects.create(**validated_data)

class GetDirectionsSerializer(serializers.ModelSerializer):
    # from_location = serializers.PrimaryKeyRelatedField(read_only=True)
    # to_location = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Directions
        fields = ('pk', 'from_location', 'to_location')

class GetParcelInfoSerializer(serializers.ModelSerializer):
    envelope = EnvelopeSerializer()
    options = ParcelOptionSerializer()
    class Meta:
        model = ParcelInfo
        fields = ('pk', 'envelope', 'width','lenght' , 'hight', 'weight', 'options', )

class GetParcelDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelDate
        fields = ('pk','create_time','delivery_time',)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('firs_name', 'last_name', 'phone',)

class GetDataSerializer(serializers.ModelSerializer):

    sender =  UserSerializer
    location_info = DirectionsSerializer
    parcel_info = GetParcelInfoSerializer
    delivery_type = DeliveryTypeSerializer
    package_type = PackageTypeSerializer
    create_at = ParcelDateSerializer
    recipient_info = RecipientSerializer

    class Meta:
        model = Parcel
        fields = ('pk', 'code','location_info', 'parcel_info', 'delivery_type', 'sender', 'package_type','create_at', 'recipient_info',)
    def create(self, validated_data):
        directions = validated_data.pop('location_info')
        Directions.objects.create(from_location=directions.from_location, to_location=directions.to_location)
        delivery_type = validated_data.pop('delivery_type')
        DeliveryType.objects.create(name=delivery_type.name)
        return Parcel.objects.create(**validated_data)