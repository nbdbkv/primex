from django import forms

from account.models import User
from account.choices import UserRole


class UserAdminForm(forms.ModelForm):
    role = forms.IntegerField(initial=UserRole.COURIER, disabled=True)
    region = forms.IntegerField(disabled=True)

    class Meta:
        model = User
        fields = ('phone', 'password', 'first_name', 'last_name', 'patronymic', 'region', 'city', 'role')
