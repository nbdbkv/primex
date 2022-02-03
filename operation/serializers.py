from rest_framework import serializers
from .models import Parcel

class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = '__all__'

class ParcelPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('price',)

class ParcelPaymentWithBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ('price',)
