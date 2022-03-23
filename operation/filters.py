from django_filters import FilterSet, NumberFilter
from django.shortcuts import get_object_or_404

from operation.models import Envelop, District


def get_from_district(queryset, name, value):
    lookup = "distance__from_region"
    region = get_object_or_404(District.objects, id=value).region
    return queryset.filter(**{lookup: region})


class EnvelopFilter(FilterSet):
    from_district = NumberFilter(method=get_from_district)
    to_district = NumberFilter(
        field_name="distance__to_district", lookup_expr="distance__to_district"
    )

    class Meta:
        model = Envelop
        fields = ["from_district", "to_district"]

    def get_from_district(self, queryset, name, value):
        lookup = "distance__from_region"
        region = get_object_or_404(District.objects, id=value).region
        return queryset.filter(**{lookup: region})
