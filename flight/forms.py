from django import forms

from .choices import get_status
from .models import Flight, Arrival


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
