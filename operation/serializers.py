from rest_framework import serializers
from .models import (Parcel, Directions, Direction, ParcelInfo, DeliveryType, Envelope, Recipient, ParcelDate, UserInfo, Town, Area, Package, ParcelOption)
from account.models import User

class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        # fields = ('pk', 'price', 'code', 'location_info', 'parcel_info', 'delivery_type', 'sender_info', 'package_type', 'create_at', 'delivery_date', 'recipient_info', 'sender', 'status' )
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
    area = AreaSerializer()
    town = TownSeralizer()
    class Meta:
        model = Direction
        fields = ('town', 'area','street', 'number',)

class GetDirectionsSerializer(serializers.ModelSerializer):
    from_location = GetDirectionSerializer()
    to_location = GetDirectionSerializer()
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

class GetDataSerializer(serializers.ModelSerializer):
    sender = SenderSerializer()
    location_info = GetDirectionsSerializer()
    parcel_info = GetParcelInfoSerializer()
    delivery_type = DeliveryTypeSerializer()
    package_type = PackageTypeSerializer()
    create_at = GetParcelDateSerializer()
    recipient_info = RecipientSerializer()
    class Meta:
        model = Parcel
        fields = ('pk', 'code','location_info', 'parcel_info', 'delivery_type', 'sender', 'package_type','create_at', 'recipient_info',)
