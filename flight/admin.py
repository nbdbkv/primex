from django.contrib import admin

from flight.models import Flight, Box, BaseParcel


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('numeration', 'created_at', 'code', 'quantity',
                    'weight', 'cube', 'density', 'consumption',
                    'price', 'sum', 'status')
    exclude = ('weight', 'cube', 'density', 'consumption', 'price', 'sum')


class BaseParcelInline(admin.StackedInline):
    model = BaseParcel
    extra = 1


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'code', 'track_code', 'weight', 'consumption')
    exclude = ('box', 'weight')
    inlines = [BaseParcelInline]

    def save_model(self, request, obj, form, change):
        a = 0
        sum = 0.0
        for key, value in form.data.items():
            if key == f'base_parcel-{a}-weight':
                if value:
                    sum += float(value)
                    a += 1
                    super().save_model(request, obj, form, change)
        obj.weight = sum
        super(BoxAdmin, self).save_model(request, obj, form, change)


