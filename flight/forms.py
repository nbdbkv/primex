from django import forms
from django.core.exceptions import ValidationError

from account.models import User
from .choices import get_status
from .models import Flight, Arrival, Delivery


class BaseParcelModelForm(forms.ModelForm):

    class Meta:
        widgets = {
            'track_code': forms.TextInput(attrs={'size': '20'}),
            'client_code': forms.TextInput(attrs={'size': '12'}),
            'phone': forms.TextInput(attrs={'size': '18'}),
            'price': forms.NumberInput(attrs={'style': 'width:6ch', 'readonly': 'readonly'}),
            'weight': forms.NumberInput(attrs={'style': 'width:9ch'}),
            'cost_usd': forms.NumberInput(attrs={'style': 'width:8ch', 'readonly': 'readonly'}),
        }

    # def clean_client_code(self):
    #     client_code = self.cleaned_data['client_code']
    #     code_logistics = User.objects.filter(role=1).values_list('code_logistic', flat=True)
    #     if client_code not in code_logistics:
    #         raise ValidationError(f"Клиент с кодом {client_code} не существует")
    #     else:
    #         return self.cleaned_data['client_code']
    #
    # def clean_phone(self):
    #     phone = self.cleaned_data['phone']
    #     if phone:
    #         phones = User.objects.filter(role=1).values_list('phone', flat=True)
    #         if phone not in phones:
    #             raise ValidationError(f"Клиент с телефонным номером {phone} не существует")
    #         else:
    #             return self.cleaned_data['phone']


class BoxModelForm(forms.ModelForm):

    class Meta:
        widgets = {
            'code': forms.TextInput(attrs={'size': '12', 'readonly': 'readonly'}),
            'track_code': forms.TextInput(attrs={'size': '10', 'readonly': 'readonly'}),
            'weight': forms.NumberInput(attrs={'style': 'width:10ch'}),
            'comment': forms.Textarea(attrs={'rows': '1', 'cols': '40'}),
        }


class FlightBaseParcelModelForm(forms.ModelForm):

    class Meta:
        widgets = {
            'track_code': forms.TextInput(attrs={'size': '20', 'readonly': 'readonly'}),
            'client_code': forms.TextInput(attrs={'size': '12'}),
            'phone': forms.TextInput(attrs={'size': '18'}),
            'price': forms.NumberInput(attrs={'style': 'width:6ch', 'readonly': 'readonly'}),
            'weight': forms.NumberInput(attrs={'style': 'width:9ch', 'readonly': 'readonly'}),
            'cost_usd': forms.NumberInput(attrs={'style': 'width:8ch', 'readonly': 'readonly'}),
        }


class FlightBoxModelForm(forms.ModelForm):
    swap = forms.ModelChoiceField(
        required=False,
        label='Рейс',
        queryset=Flight.objects.filter(status=0)
    )

    class Meta:
        widgets = {
            'number': forms.TextInput(attrs={'size': '4', 'readonly': 'readonly'}),
            'code': forms.TextInput(attrs={'size': '12', 'readonly': 'readonly'}),
            'track_code': forms.TextInput(attrs={'size': '10', 'readonly': 'readonly'}),
            'weight': forms.NumberInput(attrs={'style': 'width:10ch'}),
            'comment': forms.Textarea(attrs={'rows': '1', 'cols': '40'}),
        }


class FlightModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FlightModelForm, self).__init__(*args, **kwargs)
        self.fields["status"].widget = forms.Select(choices=get_status()[0:3])

    class Meta:
        model = Flight
        fields = ('numeration', 'code', 'status',)


class ArrivalModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ArrivalModelForm, self).__init__(*args, **kwargs)
        self.fields["status"].widget = forms.Select(choices=get_status()[2:5])

    class Meta:
        model = Arrival
        fields = ('numeration',  'code', 'status',)


class DeliveryModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DeliveryModelForm, self).__init__(*args, **kwargs)
        self.fields["status"].widget = forms.Select(choices=get_status()[4:6])

    class Meta:
        model = Delivery
        fields = ('numeration',  'code', 'status',)
