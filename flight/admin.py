from django.contrib import admin

from flight.models import Flight, Box, BaseParcel
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields, widgets


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('numeration', 'created_at', 'code', 'quantity',
                    'weight', 'cube', 'density', 'consumption', 'status')
    exclude = ('weight', 'cube', 'density', 'consumption')


class BaseParcelInline(admin.StackedInline):
    model = BaseParcel
    extra = 1


class BoxAdminResource(resources.ModelResource):
    created_at = fields.Field(
        column_name='ДАТА',
        attribute='created_at',
        widget=widgets.DateWidget('%d-%b-%Y')
    )
    code = fields.Field(
        column_name='КОД',
        attribute='code',
        widget=widgets.CharWidget())
    track_code = fields.Field(
        column_name='ТРЕК',
        attribute='track_code',
        widget=widgets.CharWidget()
    )
    weight = fields.Field(
        column_name='ВЕС',
        attribute='weight'
    )

    price = fields.Field(
        column_name='ЦЕНА',
        attribute='price',
    )
    consumption = fields.Field(
        column_name='РАСХОД',
        attribute='consumption'
    )
    sum = fields.Field(
        column_name='СУММА',
        attribute='sum'
    )
    comment = fields.Field(
        column_name='ПРИМЕЧАНИЕ',
        attribute='comment'
    )

    class Meta:
        model = Box
        import_id_fields = ['track_code']
        fields = ('created_at', 'code', 'track_code', 'weight', 'price', 'consumption', 'sum', 'comment')


@admin.register(Box)
class BoxAdmin(ImportExportModelAdmin):
    list_display = ('created_at', 'code', 'track_code', 'weight', 'consumption')
    exclude = ('box',)
    resource_class = BoxAdminResource
    inlines = [BaseParcelInline]
    change_list_template = "admin/box_change_list.html"

    def changelist_view(self, request, extra_context=None):
        flight = Flight.objects.all()
        extra_context = extra_context or {}
        extra_context['flights'] = flight
        return super(BoxAdmin, self).changelist_view(request, extra_context=extra_context)