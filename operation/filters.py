from django_filters import FilterSet, NumberFilter

from operation.models import Envelop


class EnvelopFilter(FilterSet):
    from_district = NumberFilter(field_name='distance__from_region__district', lookup_expr='distance__from_region__district')
    to_district = NumberFilter(field_name='distance__to_district', lookup_expr='distance__to_district') 

    class Meta:
        model = Envelop 
        fields = ['from_district', 'to_district']
