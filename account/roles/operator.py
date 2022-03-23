from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django import forms

from account.models import Region, User
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
        )


def get_permission():
    content_type = ContentType.objects.get_for_model(User, for_concrete_model=False)
    operator_permissions = Permission.objects.filter(content_type=content_type)
    return operator_permissions
