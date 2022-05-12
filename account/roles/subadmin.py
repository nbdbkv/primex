import requests
from django.contrib.auth.models import Group
from django import forms
from django.db.models import IntegerChoices

from account.models import User, Region, District
from account.choices import UserRole, SubAdminRole


class SubadminUserRole(IntegerChoices):
    COURIER = UserRole.COURIER.value
    OPERATOR = UserRole.OPERATOR.value


class UserAdminForm(forms.ModelForm):
    role = forms.ChoiceField(choices=SubAdminRole.choices)

    class Meta:
        model = User
        fields = (
            "phone",
            "password",
            "info",
            "role",
            "is_active",
            "is_staff",
            "groups",
        )


    def save(self, **kwargs):
        try:
            user_phone = kwargs.pop('user')
            user_region = User.objects.get(phone=user_phone).region
            user_district = User.objects.get(phone=user_phone).district
            instance = super(UserAdminForm, self).save(**kwargs)
            instance.region = user_region
            instance.district = user_district
        except:
            print("Some thing went wrong!!!")
        finally:
            instance = super(UserAdminForm, self).save(**kwargs)
        return instance

def get_group():
    group = Group.objects.get(name="Subadmin")
    return group
