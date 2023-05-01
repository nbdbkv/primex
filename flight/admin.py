from datetime import datetime

from django.contrib import admin
from django.contrib.admin import AdminSite, DateFieldListFilter
from django.db import models
from django.db.models import Sum, Q
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _

import nested_admin
from rangefilter.filters import DateTimeRangeFilter

from flight.forms import FlightModelForm, ArrivalModelForm, BaseParcelModelForm, FlightBoxModelForm
from flight.models import Flight, Box, BaseParcel, Arrival, Archive, Unknown
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields, widgets

original_get_app_list = AdminSite.get_app_list


class FlightBaseParcelInline(nested_admin.NestedTabularInline):
    model = BaseParcel
    form = BaseParcelModelForm
    exclude = ('status',)
    template = 'admin/flight_baseparcel_tabular.html'
    extra = 0
    classes = ('collapse',)


class FlightBoxInline(nested_admin.NestedTabularInline):
    model = Box
    form = FlightBoxModelForm
    exclude = ('status',)
    template = 'admin/flight_box_tabular.html'
    extra = 0
    inlines = (FlightBaseParcelInline,)


@admin.register(Flight)
class FlightAdmin(nested_admin.NestedModelAdmin):
    form = FlightModelForm
    list_display = ('numeration', 'code', 'sum_box_quantity', 'sum_weight', 'cube', 'density', 'consumption',
                    'status', 'created_at', )
    list_display_links = ('numeration', 'code',)
    exclude = ('weight', 'cube', 'density', 'consumption', 'price', 'sum', 'quantity',)
    search_fields = ['box__code', 'box__base_parcel__code', 'code']
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter))
    inlines = (FlightBoxInline,)

    def get_queryset(self, request):
        return Flight.objects.filter(status__in=[0, 1])

    @admin.display(description=_('Кол. коробок'))
    def sum_box_quantity(self, obj):
        box_quantity = Box.objects.filter(flight_id=obj.id).count()
        return box_quantity

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
    readonly_fields = ('code', 'track_code', 'weight',)
    fields = (readonly_fields, 'status',)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class ArchiveBaseParcelNestedInline(nested_admin.NestedTabularInline):
    model = BaseParcel
    readonly_fields = ('code', 'track_code', 'weight', 'status',)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class BoxNestedInline(nested_admin.NestedTabularInline):
    model = Box
    readonly_fields = ('code', 'track_code', 'weight', 'price', 'consumption', 'sum', 'comment',)
    fields = (readonly_fields, 'status',)
    inlines = (BaseParcelNestedInline,)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class ArchiveBoxNestedInline(nested_admin.NestedTabularInline):
    model = Box
    readonly_fields = ('code', 'track_code', 'weight', 'price', 'consumption', 'sum', 'comment', 'status')
    inlines = (ArchiveBaseParcelNestedInline,)

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
    readonly_fields = ('numeration', 'code', 'quantity', 'sum_boxes', 'weight', 'sum_parcel_weights',)
    fields = [readonly_fields, 'status']
    change_form_template = "admin/arrival_change_form.html"

    @admin.display(description=_('Коробки по прибытии'))
    def sum_boxes(self, obj):
        boxes = Box.objects.filter(flight_id=obj.id).count()
        return boxes

    @admin.display(description=_('Вес (роздан)'))
    def sum_parcel_weights(self, obj):
        weight = BaseParcel.objects.filter(box__flight_id=obj.id, status=5).aggregate(Sum('weight'))
        return weight['weight__sum']

    def get_queryset(self, request):
        return Arrival.objects.filter(status__in=[2, 3, 4])

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def if_change(self, obj):
        if obj.status == 5:
            obj.is_archive = True
            obj.save()
            for box in obj.box.filter(~Q(status=obj.status)):
                box.status = 7
                box.save()
                for p in box.base_parcel.filter(~Q(status=obj.status)):
                    p.status = 7
                    p.save()
        else:
            self.change_statuses(obj)

    def change_statuses(self, obj):
        for box in obj.box.filter(~Q(status=obj.status)):
            box.status = obj.status
            box.save()
            for p in box.base_parcel.filter(~Q(status=obj.status)):
                p.status = obj.status
                p.save()

    def save_model(self, request, obj, form, change):
        super(ArrivalAdmin, self).save_model(request, obj, form, change)
        if form.has_changed():
            self.if_change(obj)
        else:
            for i in request.POST.getlist('boxes'):
                box = Box.objects.get(id=int(eval(i)['box']))
                box.status = int(eval(i)['status'])
                box.save()
            for i in request.POST.getlist('base_parcels'):
                base_parcel = BaseParcel.objects.get(id=int(eval(i)['base_parcel']))
                base_parcel.status = int(eval(i)['status'])
                base_parcel.save()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context)


@admin.register(Archive)
class ArchiveAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        'numeration', 'created_at', 'code', 'quantity', 'weight', 'cube', 'density', 'consumption', 'status',
    )
    search_fields = ('numeration', 'box__code', 'box__base_parcel__code',)
    date_hierarchy = 'created_at'
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter))
    inlines = (ArchiveBoxNestedInline,)
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
    list_display = ('code', 'track_code', 'weight',)
    search_fields = ('code',)
    date_hierarchy = 'created_at'
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter))

    def get_queryset(self, request):
        return Unknown.objects.filter(status=7)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BaseParcelInline(admin.TabularInline):
    model = BaseParcel
    form = BaseParcelModelForm
    exclude = ('status',)
    template = 'admin/box_baseparcel_tabular.html'
    extra = 50


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
    list_display = (
        'number', 'created_at', 'code', 'track_code', 'sum_baseparcel_quantity', 'weight', 'get_total_consumption',
        'sum_baseparcel_consumption',
    )
    list_display_links = ('number', 'created_at', 'code', 'track_code',)
    exclude = ('number', 'box', 'status',)
    date_hierarchy = 'created_at'
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter),)
    search_fields = ('base_parcel__code',)
    resource_class = BoxAdminResource
    inlines = (BaseParcelInline,)
    # change_list_template = "admin/box_change_list.html"
    change_form_template = "admin/box_change_form.html"
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': '3', 'cols': '34'})},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "flight":
            kwargs["queryset"] = Flight.objects.filter(status=0)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            box = Box.objects.last()
            if box.created_at.day == datetime.now().day:
                obj.number = box.number + 1
            else:
                obj.number = 1
        super(BoxAdmin, self).save_model(request, obj, form, change)

    @admin.display(description=_('Кол. посылок'))
    def sum_baseparcel_quantity(self, obj):
        baseparcel_quantity = BaseParcel.objects.filter(box_id=obj.id).count()
        return baseparcel_quantity

    @admin.display(description=_('Вес посылок'))
    def sum_baseparcel_weight(self, obj):
        baseparcel_weight = BaseParcel.objects.filter(box_id=obj.id).aggregate(Sum('weight'))
        return baseparcel_weight['weight__sum']

    @admin.display(description=_('Общий расход $'))
    def get_total_consumption(self, obj):
        if obj.consumption:
            total_consumption = obj.consumption + self.sum_baseparcel_consumption(obj)
        else:
            total_consumption = None
        return total_consumption

    @admin.display(description=_('Доп. расход $'))
    def sum_baseparcel_consumption(self, obj):
        baseparcel_consumption = BaseParcel.objects.filter(box_id=obj.id).aggregate(Sum('consumption'))
        return baseparcel_consumption['consumption__sum']

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


# @admin.register(BaseParcel)
class BaseParselAdmin(admin.ModelAdmin):
    list_display = ('code', 'track_code', 'weight', 'created_at',)
    exclude = ('status',)
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter),)
    change_list_template = "admin/box_parcel_change_list.html"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "box":
            kwargs["queryset"] = Box.objects.filter(status=None)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        return qs.filter(box=None)

    def changelist_view(self, request, extra_context=None):
        parcel = Box.objects.filter(status=None)
        extra_context = extra_context or {}
        extra_context['boxes'] = parcel
        return super(BaseParselAdmin, self).changelist_view(request, extra_context=extra_context)
