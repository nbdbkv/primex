from django.contrib.auth.models import Group
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
        fields = ("phone", "password", "info", "region", "district", "role")


def get_group():
    group = Group.objects.get(name="Subadmin")
    return group
