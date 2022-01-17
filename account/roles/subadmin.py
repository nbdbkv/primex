from django import forms
from django.db.models import IntegerChoices

from account.models import User
from account.choices import UserRole


class SubadminUserRole(IntegerChoices):
    COURIER = UserRole.COURIER.value
    OPERATOR = UserRole.OPERATOR.value


class UserAdminForm(forms.ModelForm):
    role = forms.ChoiceField(choices=SubadminUserRole)

    class Meta:
        model = User
        fields = ('phone', 'password', 'first_name', 'last_name', 'patronymic', 'region', 'city', 'role')