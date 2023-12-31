import random
from io import BytesIO

import qrcode
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils.translation import ugettext_lazy as _
from fcm_django.models import FCMDevice
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from transliterate import translit

from account.choices import SendCodeType
from account.messages import ErrorMessage
from account.models import District, MobileCode, Region, User, Village, AppVersion


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("phone", "password", "info", "region")

    def validate_phone(self, phone):
        code = phone[3:6]
        mobile_code = MobileCode.objects.filter(operator=code)
        if not mobile_code:
            raise ValidationError(ErrorMessage.PHONE_VERIFY.value)
        else:
            return phone

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.set_password(validated_data["password"])
        instance.save()
        return instance


# class UserSendCodeSerializer(serializers.Serializer):
#     phone = serializers.CharField(validators=[PhoneValidator], required=True)
#     # token = serializers.CharField(required=False)
#     type = serializers.ChoiceField(choices=SendCodeType.choices, default=1, required=False)
#
#     class Meta:
#         fields = ('phone', 'token', 'type')
#
#     def validate(self, attrs):
#         print('*' * 50, attrs)
#         if attrs["type"] == SendCodeType.RESET_PHONE:
#             return attrs
#         try:
#             self.instance = User.objects.get(phone=attrs["phone"])
#             return attrs
#         except User.DoesNotExist:
#             raise ValidationError(ErrorMessage.USER_NOT_EXISTS.value)

    # def send_otp_code(self):
    #     data = self.validated_data
    #     phone = data["phone"]
    #     code = get_otp()
    #     print(code)
    #     cache.set(code, phone, settings.SMS_CODE_TIME, version=data["type"])
    #     SendSMS(phone, f"code: {code}").send


class RegisterCodeVerifySerializer(serializers.Serializer):
    code = serializers.IntegerField(required=True)

    def validate(self, attrs):
        phone = cache.get(attrs["code"], version=SendCodeType.REGISTER)
        if phone is not None:
            self.instance = User.objects.get(phone=phone)
            return attrs
        raise ValidationError(ErrorMessage.WRONG_OTP.value)

    def generate_qr(self, user, code=None):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        if code:
            qr.add_data(code)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer)
            buffer.seek(0)
            user.qr_logistic.save(f'{code}.png', File(buffer), save=True)
        else:
            qr.add_data(user.phone)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer)
            buffer.seek(0)
            user.qr_phone.save(f'{user.phone}.png', File(buffer), save=True)

    def generate_code_logistic(self, user):
        startswith = user.region.name
        text = translit(startswith, language_code='ru', reversed=True)
        random_number = random.randint(11111, 99999)
        while User.objects.filter(code_logistic__endswith=str(random_number)).exists():
            random_number -= 1
        else:
            code_logistic = text.upper()[:4] + str(random_number)
            user.code_logistic = code_logistic
            user.save()
        self.generate_qr(user, code_logistic)

    def update(self):
        self.instance.is_active = True
        self.instance.save()
        self.generate_qr(self.instance)
        self.generate_code_logistic(self.instance)
        return self.instance


class PasswordUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('password', 'new_password')

    def validate(self, attrs):
        user = self.context['request'].user
        password = attrs.get('password')
        new_password = attrs.get('new_password')
        if not user.check_password(password):
            raise serializers.ValidationError(ErrorMessage.PASSWORD_ERROR.value)
        try:
            validate_password(new_password, user)
        except ValidationError as exc:
            raise ValidationError(ErrorMessage.PASSWORD_VALID.value)
        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data.get('new_password')
        instance.set_password(new_password)
        instance.save()
        return instance


class PasswordResetVerifySerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        phone = cache.get(attrs["code"], version=SendCodeType.RESET_PASSWORD)
        if phone is not None:
            self.instance = User.objects.get(phone=phone)
            return attrs
        raise ValidationError(ErrorMessage.WRONG_OTP.value)

    def validate_password(self, password):
        try:
            validate_password(password)
            return password
        except ValidationError as exc:
            raise ValidationError(ErrorMessage.PASSWORD_VALID.value)

    class Meta:
        model = User
        fields = ('phone', 'code', 'password')


class PhoneResetVerifySerializer(serializers.Serializer):
    code = serializers.CharField(required=True)

    def validate(self, attrs):
        phone = cache.get(attrs["code"], version=SendCodeType.RESET_PHONE)
        if phone is not None:
            attrs["new_phone"] = phone
            return attrs
        raise ValidationError(ErrorMessage.WRONG_OTP.value)

    def update(self, instance):
        instance.phone = self.validated_data["new_phone"]
        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    default_error_messages = {
        'no_active_account': _('Неверный телефон или пароль.')
    }


class UpdateUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("info", "region", "district", "avatar")


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            "role",
            "is_active",
            "is_staff",
            "date_joined",
            "password",
            "last_login",
            "is_superuser",
            "groups",
            "user_permissions",
        )


class DistrictsSerializer(serializers.ModelSerializer):
    region = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = District
        fields = "__all__"


class VillagesSerializer(serializers.ModelSerializer):
    region = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Village
        fields = "__all__"


class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = ('android_version', 'android_is_updated', 'ios_version', 'ios_is_updated')


class RegionsSerializer(serializers.ModelSerializer):
    district_set = DistrictsSerializer(many=True)
    village_set = VillagesSerializer(many=True)

    class Meta:
        model = Region
        fields = "__all__"


class FcmCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = '__all__'


class PhoneVerifySerializer(serializers.ModelSerializer):
    token = serializers.CharField()

    class Meta:
        model = User
        fields = ('phone', 'token')


class LoginGoogleSerializer(serializers.ModelSerializer):
    token = serializers.CharField()
    full_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('token', 'full_name')


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'first_name', 'last_name', 'region')


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("code_logistic",  "phone")
