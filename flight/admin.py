from django.contrib import admin
from django.contrib.admin import AdminSite, DateFieldListFilter
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.db.models import Q

import nested_admin
from rangefilter.filters import DateTimeRangeFilter

from flight.forms import FlightModelForm, ArrivalModelForm, MyInlineForm
from flight.models import Flight, Box, BaseParcel, Arrival, Archive, Unknown
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields, widgets

original_get_app_list = AdminSite.get_app_list


class BoxInline(admin.StackedInline):
    model = Box
    exclude = ('status',)
    extra = 0



@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    form = FlightModelForm
    list_display = ('numeration', 'code', 'quantity', 'sum_weight', 'cube', 'density', 'consumption',
                    'status', 'created_at', )
    exclude = ('weight', 'cube', 'density', 'consumption', 'price', 'sum')
    search_fields = ['box__code', 'box__base_parcel__code', 'code']
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter))

    inlines = [BoxInline]

    def get_queryset(self, request):
        return Flight.objects.filter(status__in=[0, 1, 2])

    @admin.display(description=_('Вес'))
    def sum_weight(self, obj):
        weight = Box.objects.filter(flight_id=obj.id).aggregate(Sum('weight'))
        return weight['weight__sum']

    def save_model(self, request, obj, form, change):
        a = 0
        sum = 0.0
        for key, value in form.data.items():
            if key == f'box-{a}-weight':
                if value:
                    sum += float(value)
                    a += 1
        obj.weight = sum
        super(FlightAdmin, self).save_model(request, obj, form, change)


class BaseParcelNestedInline(nested_admin.NestedTabularInline):
    model = BaseParcel
    readonly_fields = ('code', 'track_code', 'weight', 'width', 'length', 'height',)
    fields = (readonly_fields, 'status',)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class ArchiveBaseParcelNestedInline(nested_admin.NestedTabularInline):
    model = BaseParcel
    readonly_fields = ('code', 'track_code', 'weight', 'width', 'length', 'height', 'status')

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class BoxNestedInline(nested_admin.NestedTabularInline):
    model = Box
    readonly_fields = ('code', 'track_code', 'weight', 'price', 'consumption', 'sum', 'comment',)
    fields = (readonly_fields, 'status')
    inlines = [BaseParcelNestedInline]

    
    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class ArchiveBoxNestedInline(nested_admin.NestedTabularInline):
    model = Box
    readonly_fields = ('code', 'track_code', 'weight', 'price', 'consumption', 'sum', 'comment', 'status')
    inlines = [ArchiveBaseParcelNestedInline]

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
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter))
    inlines = [BoxNestedInline]

    def get_queryset(self, request):
        return Arrival.objects.filter(status__in=[2, 3, 4, 5])

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def change_statuses(self, obj, status):
        for box in obj.box.filter(~Q(status=int(status))):
            box.status = int(status)
            box.save()
            for p in box.base_parcel.filter(~Q(status=int(status))):
                p.status = int(status)
                p.save()

    def save_model(self, request, obj, form, change):
        super(ArrivalAdmin, self).save_model(request, obj, form, change)
        status = form.data.get('status')

        if status == '5':
            obj.is_archive = True
            obj.save()
            box_index = 0
            for key, value in form.data.items():
                if key == f'box-{box_index}-status':
                    if value != '5':
                        box = Box.objects.get(id=int(form.data.get(f'box-{box_index}-id')))
                        box.status = 7
                        box.save()
                        for p in box.base_parcel.filter(~Q(status=5)):
                            p.status = 7
                            p.save()
                        box_index += 1
        else:
            self.change_statuses(obj, status)
@admin.register(Archive)
class ArchiveAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        'numeration', 'created_at', 'code', 'quantity', 'weight', 'cube', 'density', 'consumption', 'status',
    )
    search_fields = ('numeration', 'box__code', 'box__base_parcel__code',)
    date_hierarchy = 'created_at'
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter))
    inlines = [ArchiveBoxNestedInline]
    exclude = ('is_archive',)
    readonly_fields = (
        'numeration', 'created_at', 'code', 'quantity', 'weight', 'cube', 'density', 'consumption', 'status',)

    def get_queryset(self, request):
        return Archive.objects.filter(is_archive=True)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = dict(show_save=False, show_save_and_continue=False, show_delete=False)
        template_response = super().change_view(request, object_id, form_url, extra_context)
        return template_response


@admin.register(Unknown)
class UnknownAdmin(nested_admin.NestedModelAdmin):
    list_display = ('code', 'track_code', 'weight', 'width', 'length', 'height')
    search_fields = ('code',)
    date_hierarchy = 'created_at'
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter))

    def get_queryset(self, request):
        return Unknown.objects.filter(status=7)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BaseParcelInline(admin.StackedInline):
    model = BaseParcel
    exclude = ('status',)
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
    list_display = ('code', 'track_code', 'sum_weight', 'consumption', 'created_at',)
    exclude = ('box', 'status',)
    resource_class = BoxAdminResource
    inlines = [BaseParcelInline]
    change_list_template = "admin/box_change_list.html"

    @admin.display(description=_('Вес'))
    def sum_weight(self, obj):
        weight = BaseParcel.objects.filter(box_id=obj.id).aggregate(Sum('weight'))
        return weight['weight__sum']

    def save_model(self, request, obj, form, change):
        a = 0
        sum = 0.0
        for key, value in form.data.items():
            if key == f'base_parcel-{a}-weight':
                if value:
                    sum += float(value)
                    a += 1
        obj.weight = sum
        super(BoxAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        return qs.filter(flight=None)

    def changelist_view(self, request, extra_context=None):
        flight = Flight.objects.filter(status=0)
        extra_context = extra_context or {}
        extra_context['flights'] = flight
        return super(BoxAdmin, self).changelist_view(request, extra_context=extra_context)


class AdminSiteExtension(AdminSite):
    def get_app_list(self, request):
        app_list = original_get_app_list(self, request)
        ordering = {
            "BaseParcel": 0,
            "Box": 1,
            "Flight": 2,
            "Arrival": 3,
            "Unknown": 4,
            "Archive": 5,
        }
        for idx, app in enumerate(app_list):
            if app['app_label'] == 'flight':
                app['models'].sort(key=lambda x: ordering[x['object_name']])
                flight = app_list.pop(idx)
                app_list.insert(0, flight)
                return app_list


AdminSite.get_app_list = AdminSiteExtension.get_app_list


@admin.register(BaseParcel)
class BaseParselAdmin(admin.ModelAdmin):
    list_display = ('code', 'track_code', 'weight', 'width', 'length', 'height', 'created_at',)
    exclude = ('status',)
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter),)
    change_list_template = "admin/box_parcel_change_list.html"

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        return qs.filter(box=None)

    def changelist_view(self, request, extra_context=None):
        parcel = Box.objects.filter(status=None)
        extra_context = extra_context or {}
        extra_context['boxes'] = parcel
        return super(BaseParselAdmin, self).changelist_view(request, extra_context=extra_context)
