from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
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
        fields = ('phone', 'password', 'info', 'region', 'district', 'role')
    
    
def get_permission():
    exclude_content_type = ContentType.objects.filter(model='PaymentHistory')
    temp = Permission.objects.filter(content_type=exclude_content_type) \
        .exclude(code_name='view_paymenthistory').values_list('codename', flat=True)
    operator_permissions = Permission.objects.exclude(codename__in=temp)
    return operator_permissions