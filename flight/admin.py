from django.contrib import admin
from nested_admin.nested import NestedStackedInline

from flight.models import Flight, Box, BaseParcel


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('numeration', 'created_at', 'code', 'quantity',
                    'weight', 'cube', 'density', 'consumption',
                    'price', 'sum', 'status')
    exclude = ('weight', 'cube', 'density', 'consumption', 'price', 'sum')


class BaseParcelInline(NestedStackedInline):
    model = BaseParcel
    extra = 1


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'code', 'track_code', 'weight', 'consumption')
    exclude = ('box', )
    inlines = [BaseParcelInline]



