from django.core.exceptions import ValidationError
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.contrib.auth.password_validation import validate_password
from django.conf import settings

from account.validators import PhoneValidator
from account.utils import SendSMS, get_otp
from account.choices import SendCodeType
from account.messages import ErrorMessage
from account.models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'password', 'first_name', 'last_name', 'patronymic', 'region', 'city')
    
    def validate_password(self, password):
        try:
            validate_password(password)
            return password
        except ValidationError as exc:
            raise ValidationError(ErrorMessage.PASSWORD_VALID.value)

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserSendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[PhoneValidator], required=True)
    type = serializers.ChoiceField(choices=SendCodeType.choices, required=True)

    def validate_phone(self, phone):
        try:
            self.instance = User.objects.get(phone=phone)
            return phone
        except User.DoesNotExist:
            raise ValidationError(ErrorMessage.USER_NOT_EXISTS.value)
    
    def send_otp_code(self):
        data = self.validated_data
        code = get_otp()
        print(code)
        cache.set(code, data['phone'], settings.SMS_CODE_TIME, version=data['type'])
        SendSMS()


class RegisterCodeVerifySerializer(serializers.Serializer):
    code = serializers.IntegerField(required=True)

    def validate(self, attrs):
        phone = cache.get(attrs['code'], version=SendCodeType.REGISTER)
        if phone is not None:
            self.instance = User.objects.get(phone=phone)
            return attrs
        raise ValidationError(ErrorMessage.WRONG_OTP.value)
    
    def update(self):
        self.instance.is_active = True
        self.instance.save()
        return self.instance


class PasswordResetVerifySerializer(serializers.Serializer):
    code = serializers.IntegerField(required=True)
    password = serializers.CharField(required=True)

    def validate_password(self, password):
        try:
            validate_password(password)
            return password
        except ValidationError as exc:
            raise ValidationError(ErrorMessage.PASSWORD_VALID.value)

    def validate_code(self, code):
        phone = cache.get(code, version=SendCodeType.RESET_PASSWORD)
        if phone is not None:
            self.instance = User.objects.get(phone=phone)
            return code
        raise ValidationError(ErrorMessage.WRONG_OTP.value)
    
    def update(self):
        self.instance.set_password(self.validated_data['password'])
        self.instance.save()
        return self.instance


class PhoneResetVerifySerializer(serializers.Serializer):
    code = serializers.IntegerField(required=True)

    def validate(self, attrs):
        phone = cache.get(attrs['code'], version=SendCodeType.RESET_PASSWORD)
        if phone is not None:
            attrs['new_phone'] = phone
            return attrs
        raise ValidationError(ErrorMessage.WRONG_OTP.value)
    
    def update(self, instance):
        instance.phone = self.validated_data['new_phone']
        instance.save()
        return instance


class UpdateUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'patronymic', 'region', 'city')


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'is_active', 
            'is_staff', 
            'date_joined', 
            'password', 
            'last_login',
            'is_superuser',
            'groups',
            'user_permissions')
