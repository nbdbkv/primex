from django.contrib import admin
from django.contrib.admin import AdminSite

from flight.models import Flight, Box, BaseParcel
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields, widgets

original_get_app_list = AdminSite.get_app_list


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('numeration', 'created_at', 'code', 'quantity',
                    'weight', 'cube', 'density', 'consumption',
                    'status')
    exclude = ('weight', 'cube', 'density', 'consumption', 'price', 'sum')


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


class AdminSiteExtension(AdminSite):
    def get_app_list(self, request):
        app_list = original_get_app_list(self, request)
        for idx, app in enumerate(app_list):
            if app['app_label'] == 'flight':
                flight = app_list.pop(idx)
                app_list.insert(0, flight)
                return app_list


AdminSite.get_app_list = AdminSiteExtension.get_app_list
