from django import forms

from .choices import get_status
from .models import Flight, Arrival


class BaseParcelModelForm(forms.ModelForm):

    class Meta:
        widgets = {
            'code': forms.TextInput(attrs={'size': '8'}),
            'track_code': forms.TextInput(attrs={'size': '16'}),
            'weight': forms.NumberInput(attrs={'style': 'width:10ch'}),
            'consumption': forms.NumberInput(attrs={'style': 'width:8ch'}),
        }


class FlightBoxModelForm(forms.ModelForm):

    class Meta:
        widgets = {
            'code': forms.TextInput(attrs={'size': '8'}),
            'track_code': forms.TextInput(attrs={'size': '16'}),
            'weight': forms.NumberInput(attrs={'style': 'width:10ch'}),
            'price': forms.TextInput(attrs={'size': '6'}),
            'consumption': forms.NumberInput(attrs={'style': 'width:8ch'}),
            'sum': forms.TextInput(attrs={'size': '6'}),
            'comment': forms.Textarea(attrs={'rows': '1', 'cols': '40'}),
        }


class FlightModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FlightModelForm, self).__init__(*args, **kwargs)
        self.fields["status"].widget = forms.Select(choices=get_status()[0:3])

    class Meta:
        model = Flight
        fields = ('numeration',  'code', 'quantity', 'status',)


class ArrivalModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ArrivalModelForm, self).__init__(*args, **kwargs)
        self.fields["status"].widget = forms.Select(choices=get_status()[2:6])

    class Meta:
        model = Arrival
        fields = ('numeration',  'code', 'quantity', 'status',)
