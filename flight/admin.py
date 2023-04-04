from django.contrib import admin
from django.contrib.admin import AdminSite, DateFieldListFilter

import nested_admin

from flight.forms import FlightModelForm, ArrivalModelForm
from flight.models import Flight, Box, BaseParcel, Arrival
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields, widgets

original_get_app_list = AdminSite.get_app_list


class BoxInline(admin.StackedInline):
    model = Box
    extra = 0


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    form = FlightModelForm
    list_display = ('numeration', 'created_at', 'code', 'quantity',
                    'weight', 'cube', 'density', 'consumption',
                    'status')
    inlines = [BoxInline]

    def get_queryset(self, request):
        return Flight.objects.filter(status__in=[0, 1, 2])


class BaseParcelNestedInline(nested_admin.NestedTabularInline):
    model = BaseParcel
    readonly_fields = ('code', 'track_code', 'weight', 'width', 'length', 'height',)
    fields = (readonly_fields, 'status',)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class BoxNestedInline(nested_admin.NestedTabularInline):
    model = Box
    readonly_fields = ('code', 'track_code', 'weight', 'price', 'consumption', 'sum', 'comment',)
    fields = (readonly_fields, 'status',)
    inlines = [BaseParcelNestedInline]

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


@admin.register(Arrival)
class ArrivalAdmin(nested_admin.NestedModelAdmin):
    form = ArrivalModelForm
    list_display = (
        'numeration', 'created_at', 'code', 'quantity', 'weight', 'cube', 'density', 'consumption', 'status',
    )
    search_fields = ('numeration', 'box__code', 'box__base_parcel__code',)
    date_hierarchy = 'created_at'
    list_filter = (('created_at', DateFieldListFilter),)
    inlines = [BoxNestedInline]

    def get_queryset(self, request):
        return Arrival.objects.filter(status__in=[2, 3, 4, 5])

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BaseParcelInline(admin.StackedInline):
    model = BaseParcel
    extra = 0


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

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        return qs.filter(flight=None)

    def changelist_view(self, request, extra_context=None):
        flight = Flight.objects.all()
        extra_context = extra_context or {}
        extra_context['flights'] = flight
        return super(BoxAdmin, self).changelist_view(request, extra_context=extra_context)

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
        ordering = {
            "Box": 0,
            "Flight": 1,
            "Arrival": 2,
            "Archive": 3,
            "Unknown": 4,
        }
        for idx, app in enumerate(app_list):
            if app['app_label'] == 'flight':
                app['models'].sort(key=lambda x: ordering[x['object_name']])
                flight = app_list.pop(idx)
                app_list.insert(0, flight)
                return app_list


AdminSite.get_app_list = AdminSiteExtension.get_app_list
