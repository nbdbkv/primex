from django.contrib.auth.models import Group
from django import forms

from account.models import Region, User, District
from account.choices import UserRole


class UserAdminForm(forms.ModelForm):
    role = forms.IntegerField(initial=UserRole.COURIER, disabled=True)
    region = forms.ModelChoiceField(Region.objects, disabled=True, required=False)

    class Meta:
        model = User
        fields = (
            "phone",
            "password",
            "info",
            "region",
            "district",
            "role",
            "is_active",
            "is_staff",
            "groups",
        )


def get_group():
    group = Group.objects.get(name="Operator")
    return group
