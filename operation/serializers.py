from django.core.files.base import ContentFile
from django.db.models import Q
from django.forms import ValidationError
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.db import transaction
import base64

from xlwt.compat import basestring

from account.models import User
from account.serailizers import DistrictsSerializer, VillagesSerializer
from account.validators import PhoneValidator
from operation.services import get_parcel_code, CalculateParcelPrice
from operation.choices import (
    DirectionChoices,
    PayStatusChoices,
    PaymentHistoryType,
    UserInfoChoices,
    PaymentTypeChoices,
)
from operation.models import (
    DeliveryStatus,
    ParcelOption,
    Parcel,
    Distance,
    DeliveryType,
    Packaging,
    PaymentDimension,
    Envelop,
    ParcelPayment,
    PaymentHistory,
    PaymentType,
    Payment,
    Direction,
    UserInfo,
    ParcelDimension,
    Images,
    ParcelBonus,
)


class Base64ImageField(serializers.ImageField):
    def from_native(self, data):
        if isinstance(data, basestring) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super(Base64ImageField, self).from_native(data)

class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = "__all__"
        depth = 1


class DeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryStatus
        fields = "__all__"


class ParcelOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParcelOption
        fields = "__all__"


class DistanceSerializer(serializers.ModelSerializer):
    from_district = serializers.SlugRelatedField("name", read_only=True)
    to_district = serializers.SlugRelatedField("name", read_only=True)

    class Meta:
        model = Distance
        fields = "__all__"


class DeliveryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryType
        exclude = ("distance",)


class ReDeliveryTypeSerializer(serializers.ModelSerializer):
    distance = DistanceSerializer()

    class Meta:
        model = DeliveryType
        fields = "__all__"


class PackagingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packaging
        fields = "__all__"


class PaymentDimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDimension
        fields = "__all__"


class EnvelopSerializer(serializers.ModelSerializer):
    dimension = PaymentDimensionSerializer()

    class Meta:
        model = Envelop
        exclude = ("distance",)


class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"


class ParcelPaymentSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)
    price = serializers.DecimalField(9, 2, read_only=True)
    pay_status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ParcelPayment
        fields = "__all__"

    def get_pay_status(self, instance):
        type = (
            PayStatusChoices.IN_ANTICIPATION
            if instance.pay_status == "in_anticipation"
            else PayStatusChoices.PAID
        )
        return type.label


class ParcelPaymentRetrieveSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(many=True)
    delivery_type = ReDeliveryTypeSerializer()
    packaging = PackagingSerializer(many=True)
    envelop = EnvelopSerializer()

    class Meta:
        model = ParcelPayment
        fields = "__all__"


class DirectionSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Direction
        fields = "__all__"


class DirectionRetrieveSerializer(DirectionSerializer):
    district = DistrictsSerializer()
    village = VillagesSerializer()
    type = serializers.SerializerMethodField()

    def get_type(self, instance):
        type = DirectionChoices.FROM if instance.type == 1 else DirectionChoices.TO
        return type.label


class UserInfoSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)
    phone = serializers.CharField(validators=[PhoneValidator])

    class Meta:
        model = UserInfo
        fields = "__all__"


class ParcelDimensionSerializer(serializers.ModelSerializer):
    parcel = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ParcelDimension
        fields = "__all__"


class ReatriveParcelSerializer(serializers.ModelSerializer):
    payment = ParcelPaymentRetrieveSerializer()
    direction = DirectionRetrieveSerializer(many=True)
    user_info = UserInfoSerializer(many=True)
    dimension = ParcelDimensionSerializer()
    option = serializers.SlugRelatedField("title", read_only=True, many=True)
    bonus = serializers.SerializerMethodField()

    class Meta:
        model = Parcel
        fields = ('id','payment', 'direction','user_info','dimension','option','bonus', 'title', 'code', 'create_at','sending_date','status','courier')

    def get_bonus(self, obj):
        bonus = ParcelBonus.objects.filter(parcel=obj).first()
        if bonus:
            return bonus.bonus
        else:
            return None


class BonusHistorySerializer(serializers.ModelSerializer):
    sending_date = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    parcel_sum = serializers.SerializerMethodField()

    class Meta:
        model = PaymentHistory
        fields = "__all__"

    def get_code(self, instance):
        try:
            return instance.parcel.code
        except:
            return None

    def get_icon(self, instance):
        try:
            request = self.context.get("request")
            image = instance.parcel.payment.delivery_type.icon.url
            url = request.build_absolute_uri(image)
            return url
        except:
            return None

    def get_parcel_sum(self, instance):
        try:
            return instance.parcel.payment.price
        except:
            return None

    def get_sending_date(self, instance):
        try:
            return instance.parcel.sending_date
        except:
            return None


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Images
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        images = self.context['images']
        parcel = validated_data.pop("parcel")
        for image in images:
            img = Images.objects.create(parcel=parcel, img=image)
        return img


class CreateParcelSerializer(serializers.ModelSerializer):
    payment = ParcelPaymentSerializer()
    direction = DirectionSerializer(many=True)
    user_info = UserInfoSerializer(many=True)
    dimension = ParcelDimensionSerializer(required=False)
    code = serializers.CharField(read_only=True)

    class Meta:
        model = Parcel
        exclude = ("sender", "create_at")

    def validate_direction(self, direction):
        if len(direction) != 2:
            raise ValidationError({"message": _("direction must be 2")})
        if direction[0].get("type") != 1:
            raise ValidationError({"message": "wrong type"})
        if direction[1].get("type") != 2:
            raise ValidationError({"message": "wrong type"})
        return direction

    def validate_user_info(self, user_info):
        if len(user_info) != 2:
            raise ValidationError({"message": _("user_info must be 2")})
        if user_info[0].get("type") != 1:
            raise ValidationError({"message": "wrong type"})
        if user_info[1].get("type") != 2:
            raise ValidationError({"message": "wrong type"})
        return user_info

    @transaction.atomic
    def create(self, validated_data):
        payment = validated_data.pop("payment")
        direction = validated_data.pop("direction")
        user_info = validated_data.pop("user_info")
        dimension = validated_data.pop("dimension")

        validated_data["code"] = get_parcel_code(direction[1])
        validated_data["sender"] = self.context.get("request").user
        options = validated_data.pop("option")
        parcel = Parcel.objects.create(**validated_data)
        parcel.option.set(options)

        packaging = payment.pop("packaging")
        payment = ParcelPayment.objects.create(parcel=parcel, **payment)
        payment.packaging.set(packaging)

        for dir in direction:
            Direction.objects.create(parcel=parcel, **dir)

        for user in user_info:
            UserInfo.objects.create(parcel=parcel, **user)

        if dimension:
            dimension = ParcelDimension.objects.create(parcel=parcel, **dimension)

        payment.price = CalculateParcelPrice(parcel).price
        payment.save()

        Payment.objects.create(
            parcel=payment,
            type=PaymentType.objects.get(type=PaymentTypeChoices.CASH),
            sum=payment.price,
        )

        ParcelBonus.objects.create(
            parcel=parcel,
            bonus=(float(payment.price)*0.05)
        )

        return parcel

