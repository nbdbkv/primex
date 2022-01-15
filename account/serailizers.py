
import re
from django.core.exceptions import ValidationError
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.contrib.auth.password_validation import validate_password

from account.validators import PhoneValidator
from account.utils import SendSMS
from account.choices import SendCodeType
from account.messages import ErrorMessage
from account.models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'password', 'first_name', 'last_name', 'patronymic', 'region', 'city')

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

    def validate(self, attrs):
        return attrs


class RegisterCodeVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[PhoneValidator], required=True)
    code = serializers.IntegerField(required=True)

    def validate_phone(self, phone):
        try:
            self.instance = User.objects.get(phone=phone)
            return phone
        except User.DoesNotExist:
            raise ValidationError(ErrorMessage.USER_NOT_EXISTS.value)

    def validate(self, attrs):
        code = cache.get(attrs['phone'])
        if code == attrs['code']:
            self.instance.is_active = True
            self.instance.save()
            return attrs
        else:
            raise ValidationError(ErrorMessage.WRONG_OTP.value)


class PasswordResetVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[PhoneValidator], required=True)
    code = serializers.IntegerField(required=True)
    password = serializers.CharField(required=True)

    def validate_password(self, password):
        try:
            validate_password(password)
            return password
        except ValidationError as exc:
            raise ValidationError(ErrorMessage.PASSWORD_VALID.value)

    def validate_phone(self, phone):
        try:
            self.instance = User.objects.get(phone=phone)
            return phone
        except User.DoesNotExist:
            raise ValidationError(ErrorMessage.USER_NOT_EXISTS.value)

    def validate(self, attrs):
        code = cache.get(attrs['phone'])
        if code == attrs['code']:
            self.instance.set_password(attrs['password'])
            self.instance.save()
            return attrs
        else:
            raise ValidationError(ErrorMessage.WRONG_OTP.value)


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