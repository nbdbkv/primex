from django.forms import ValidationError
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from account.models import District, Village
from account.serailizers import DistrictsSerializer, VillagesSerializer
from account.validators import PhoneValidator
from operation.services import get_parcel_code, CalculateParcelPrice
from operation.choices import DirectionChoices, UserInfoChoices
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
    ParcelDimension,
    User,
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

class DeliveryStatusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DeliveryStatus
        fields = '__all__'
        

class ParcelOptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ParcelOption
        fields = '__all__'


class DeliveryTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DeliveryType
        fields = '__all__'


class PackagingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Packaging
        fields = '__all__'
        

class PaymentTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PaymentType
        fields = '__all__'
        

class DimensionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PaymentDimension
        fields = '__all__'


class PriceDimensionSerializer(serializers.ModelSerializer):
    dimension = DimensionSerializer()
    
    class Meta:
        model = DimensionPrice
        fields = '__all__'


class PriceEnvelopSerializer(serializers.ModelSerializer):
    envelop = serializers.SerializerMethodField()
    dimension = DimensionSerializer()
    
    class Meta:
        model = PriceEnvelop
        fields = '__all__'
    
    def get_envelop(self, instance):
        return instance.envelop.title


class PriceListSerializer(serializers.ModelSerializer):
    dimension = PriceDimensionSerializer(many=True)
    
    class Meta:
        model = PriceList
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'


class RetrievePaymentSerializer(PaymentSerializer):
    type = serializers.SlugRelatedField(slug_field='title', read_only=True)


class ParcelPaymentSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(many=True)
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)
    price = serializers.DecimalField(9, 2, read_only=True)
    price_list = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ParcelPayment
        exclude = ('pay_status',)


class RetrieveParcelPaymentSerializer(ParcelPaymentSerializer):
    payment = RetrievePaymentSerializer(many=True)
    delivery_type = DeliveryTypeSerializer()
    packaging = PackagingSerializer(many=True)
    envelop = PriceEnvelopSerializer()


class DirectionSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Direction
        fields = '__all__'


class RetrieveDirectionSerializer(DirectionSerializer):
    district = DistrictsSerializer()
    village = VillagesSerializer()
    type = serializers.SerializerMethodField()
    
    def get_type(self, instance):
        choice = DirectionChoices
        return choice.choices[0] if instance.type == choice.FROM else choice.TO


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


class RetrieveParcelSerializer(serializers.ModelSerializer):
    payment = RetrieveParcelPaymentSerializer()
    direction = RetrieveDirectionSerializer(many=True)
    user_info = UserInfoSerializer(many=True)
    dimension = ParcelDimensionSerializer()
    option = serializers.SlugRelatedField(many=True, slug_field='title', read_only=True)
    status = DeliveryStatusSerializer()
    
    class Meta:
        model = Parcel
        fields = '__all__'


class CreateParcelSerializer(serializers.ModelSerializer):
    payment = ParcelPaymentSerializer()
    direction = DirectionSerializer(many=True)
    user_info = UserInfoSerializer(many=True)
    dimension = ParcelDimensionSerializer(required=False)
    
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
    
    def validate_user_info(self, user_info):
        if len(user_info) != 2:
            raise ValidationError({'message': _('user_info must be 2')})
        if user_info[0].get('type') != 1:
            raise ValidationError({'message': 'wrong type'})
        if user_info[1].get('type') != 2:
            raise ValidationError({'message': 'wrong type'})
        return user_info
    
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
        payment = ParcelPayment.objects.create(parcel=parcel, **payment)
        payment.packaging.set(packaging)
        for parcel_pay in parcel_payments:
            Payment.objects.create(parcel=payment, **parcel_pay)
        
        for dir in direction:
            Direction.objects.create(parcel=parcel, **dir)
        
        for user in user_info:
            UserInfo.objects.create(parcel=parcel, **user)
        
        dimension = ParcelDimension.objects.create(parcel=parcel, **dimension)
        
        parcel.payment.price = CalculateParcelPrice(parcel).price
        parcel.save()
        return parcel

class GetParcelInfoSerializer(serializers.ModelSerializer):
    direction = DirectionSerializer()

    class Meta:
        model = Parcel
        fields = ('direction',)