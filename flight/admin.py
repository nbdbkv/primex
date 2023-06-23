import re

import nested_admin
from django.contrib import admin, messages
from django.contrib.admin import AdminSite, DateFieldListFilter
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from import_export import fields, resources, widgets
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateTimeRangeFilter

from flight.forms import (
    ArrivalModelForm, BaseParcelModelForm, BoxModelForm, DeliveryModelForm, FlightBaseParcelModelForm,
    FlightBoxModelForm, FlightModelForm
)
from flight.models import (
    Archive, Arrival, BaseParcel, Box, Contact, Delivery, DeliveryBaseParcel, Destination, Flight, Media, Rate, Unknown,
    OrderDescription,
)
from flight.utils import make_add_box_to_flight_action

original_get_app_list = AdminSite.get_app_list
admin.site.site_header = 'Taura Express'


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('point', 'price_per_kg', 'currency')


class FlightBaseParcelInline(nested_admin.NestedTabularInline):
    model = BaseParcel
    form = FlightBaseParcelModelForm
    exclude = ('shelf', 'status', 'arrived_at', 'barcode', 'cost_kgs', 'note', 'delivered_at')
    template = 'admin/flight_baseparcel_tabular.html'
    extra = 0
    classes = ('collapse',)

    def has_add_permission(self, request, obj):
        return False


class FlightBoxInline(nested_admin.NestedTabularInline):
    model = Box
    form = FlightBoxModelForm
    exclude = ('destination', 'status', 'arrived_at',)
    template = 'admin/flight_box_tabular.html'
    extra = 0
    inlines = (FlightBaseParcelInline,)
    fields = ('swap', 'number', 'code', 'track_code', 'weight', 'comment')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('id')

    def has_add_permission(self, request, obj):
        return False


@admin.register(Flight)
class FlightAdmin(nested_admin.NestedModelAdmin):
    form = FlightModelForm
    list_display = (
        'numeration', 'code', 'sum_box_quantity', 'sum_box_weight', 'sum_baseparcel_weight', 'sum_baseparcel_cost',
        'status', 'created_at',
    )
    list_display_links = ('numeration', 'code',)
    search_fields = ['box__code', 'box__base_parcel__track_code', 'code']
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter))
    inlines = (FlightBoxInline,)
    change_form_template = "admin/flight_change_form.html"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(status__in=[0, 1])

    @admin.display(description=_('Кол. коробок'))
    def sum_box_quantity(self, obj):
        box_quantity = Box.objects.filter(flight_id=obj.id).count()
        return box_quantity

    @admin.display(description=_('Вес коробок'))
    def sum_box_weight(self, obj):
        weight = Box.objects.filter(flight_id=obj.id).aggregate(Sum('weight'))
        return weight['weight__sum']

    @admin.display(description=_('Вес посылок'))
    def sum_baseparcel_weight(self, obj):
        baseparcel_weight = BaseParcel.objects.filter(box__flight_id=obj.id).aggregate(Sum('weight'))
        return baseparcel_weight['weight__sum']

    @admin.display(description=_('Стоим. посылок в $'))
    def sum_baseparcel_cost(self, obj):
        baseparcel_price = BaseParcel.objects.filter(box__flight_id=obj.id).aggregate(Sum('cost_usd'))
        return baseparcel_price['cost_usd__sum']

    def save_model(self, request, obj, form, change):
        form_data = form.data
        for key, value in form_data.items():
            if 'swap' in key and value:
                if int(value) != obj.id:
                    index = re.findall(r'\d+', key)
                    box_id = form_data.get(f'box-{int(*index)}-id')
                    box = Box.objects.get(id=box_id)
                    box.flight_id = int(value)
                    box.save()

        if form.has_changed():
            self.if_change(obj)
        super(FlightAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

    def if_change(self, obj):
        if obj.status == 2:
            obj.arrived_at = now()
            for box in obj.box.filter(~Q(status=obj.status)):
                box.arrived_at = now()
                box.status = obj.status
                box.save()
                for base_parcel in box.base_parcel.filter(~Q(status=obj.status)):
                    base_parcel.arrived_at = now()
                    base_parcel.status = obj.status
                    base_parcel.save()
        else:
            for box in obj.box.filter(~Q(status=obj.status)):
                box.status = obj.status
                box.save()
                for base_parcel in box.base_parcel.filter(~Q(status=obj.status)):
                    base_parcel.status = obj.status
                    base_parcel.save()


class BaseParcelNestedInline(nested_admin.NestedTabularInline):
    model = BaseParcel
    readonly_fields = ('track_code', 'client_code', 'weight',)
    fields = (readonly_fields, 'status',)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class ArchiveBaseParcelNestedInline(nested_admin.NestedTabularInline):
    model = BaseParcel
    readonly_fields = (
        'track_code', 'client_code', 'phone', 'shelf', 'price', 'weight', 'cost_usd', 'cost_kgs', 'note',
        'delivered_at', 'status',
    )
    exclude = ('arrived_at', 'barcode')

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class BoxNestedInline(nested_admin.NestedTabularInline):
    model = Box
    readonly_fields = ('code', 'track_code', 'weight', 'comment',)
    fields = (readonly_fields, 'status',)
    inlines = (BaseParcelNestedInline,)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class ArchiveBoxNestedInline(nested_admin.NestedTabularInline):
    model = Box
    readonly_fields = ('number', 'code', 'track_code', 'weight', 'comment', 'status')
    exclude = ('arrived_at', 'destination')
    inlines = (ArchiveBaseParcelNestedInline,)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


@admin.register(Arrival)
class ArrivalAdmin(nested_admin.NestedModelAdmin):
    form = ArrivalModelForm
    list_display = (
        'numeration', 'arrived_at', 'code', 'sum_boxes', 'sum_box_weight', 'sum_baseparcel_weight',
        'sum_baseparcel_cost', 'status',
    )
    list_display_links = ('numeration', 'arrived_at', 'code',)
    search_fields = (
        'numeration', 'box__code', 'box__base_parcel__track_code', 'box__base_parcel__client_code',
        'box__base_parcel__phone',
    )
    date_hierarchy = 'arrived_at'
    ordering = ('arrived_at',)
    list_filter = (('arrived_at', DateFieldListFilter), ('arrived_at', DateTimeRangeFilter))
    readonly_fields = ('numeration', 'code', 'sum_boxes', 'sum_parcel_weights')
    fields = [readonly_fields, 'status']
    change_form_template = "admin/arrival_change_form.html"

    @admin.display(description=_('Кол. коробок'))
    def sum_boxes(self, obj):
        boxes = Box.objects.filter(flight_id=obj.id).count()
        return boxes

    @admin.display(description=_('Вес коробок'))
    def sum_box_weight(self, obj):
        weight = Box.objects.filter(flight_id=obj.id).aggregate(Sum('weight'))
        return weight['weight__sum']

    @admin.display(description=_('Вес посылок'))
    def sum_baseparcel_weight(self, obj):
        baseparcel_weight = BaseParcel.objects.filter(box__flight_id=obj.id).aggregate(Sum('weight'))
        return baseparcel_weight['weight__sum']

    @admin.display(description=_('Стоим. посылок в $'))
    def sum_baseparcel_cost(self, obj):
        baseparcel_price = BaseParcel.objects.filter(box__flight_id=obj.id).aggregate(Sum('cost_usd'))
        return baseparcel_price['cost_usd__sum']

    @admin.display(description=_('Вес посылок'))
    def sum_parcel_weights(self, obj):
        weight = BaseParcel.objects.filter(box__flight_id=obj.id).aggregate(Sum('weight'))
        return weight['weight__sum']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(status__in=[2, 3])

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def change_statuses(self, obj):
        for box in obj.box.filter(~Q(status=obj.status)).prefetch_related('base_parcel'):
            box.status = obj.status
            box.save()
            for p in box.base_parcel.filter(~Q(status=obj.status)):
                p.status = obj.status
                p.save()

    def save_model(self, request, obj, form, change):
        super(ArrivalAdmin, self).save_model(request, obj, form, change)
        if form.has_changed():
            self.change_statuses(obj)
        else:
            query_dict = request.POST

            for i in query_dict:
                if 'shelf' in i:
                    base_parcel_id = i.split('_')[-1]
                    shelf = query_dict.get(f'shelf_{base_parcel_id}')
                    if shelf:
                        base_parcel = BaseParcel.objects.get(id=int(base_parcel_id))
                        base_parcel.shelf = shelf
                        base_parcel.save()

            for i in query_dict.getlist('base_parcels'):
                base_parcel = BaseParcel.objects.get(id=int(eval(i)['base_parcel']))
                base_parcel.status = int(eval(i)['status'])
                base_parcel.save()

            for i in query_dict.getlist('boxes'):
                box = Box.objects.get(id=int(eval(i)['box']))
                box.status = int(eval(i)['status'])
                box.save()
                baseparcels = BaseParcel.objects.filter(box__id=int(eval(i)['box']))
                for baseparcel in baseparcels:
                    if baseparcel.status < box.status:
                        baseparcel.status = int(eval(i)['status'])
                        baseparcel.save()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context)


@admin.register(Delivery)
class DeliveryAdmin(nested_admin.NestedModelAdmin):
    form = DeliveryModelForm
    list_display = (
        'numeration', 'arrived_at', 'code', 'sum_boxes', 'sum_box_weight', 'sum_baseparcel_weight',
        'sum_baseparcel_cost', 'status',
    )
    list_display_links = ('numeration', 'arrived_at', 'code',)
    search_fields = (
        'numeration', 'box__code', 'box__base_parcel__track_code', 'box__base_parcel__client_code',
        'box__base_parcel__phone',
    )
    date_hierarchy = 'arrived_at'
    ordering = ('arrived_at',)
    list_filter = (('arrived_at', DateFieldListFilter), ('arrived_at', DateTimeRangeFilter))
    readonly_fields = ('numeration', 'code', 'sum_boxes', 'sum_parcel_weights', 'sum_parcel_weights_distributed')
    fields = [readonly_fields, 'status']
    change_form_template = "admin/delivery_change_form.html"

    def changelist_view(self, request, extra_context=None):
        search_data = request.GET.get('q')
        url = '{}?q={}'.format(reverse('admin:flight_deliverybaseparcel_changelist'), search_data)
        if search_data:
            request.session['q'] = search_data
            return HttpResponseRedirect(url)
        else:
            return super().changelist_view(request, extra_context)

    @admin.display(description=_('Кол. коробок'))
    def sum_boxes(self, obj):
        boxes = Box.objects.filter(flight_id=obj.id).count()
        return boxes

    @admin.display(description=_('Вес коробок'))
    def sum_box_weight(self, obj):
        weight = Box.objects.filter(flight_id=obj.id).aggregate(Sum('weight'))
        return weight['weight__sum']

    @admin.display(description=_('Вес посылок'))
    def sum_baseparcel_weight(self, obj):
        baseparcel_weight = BaseParcel.objects.filter(box__flight_id=obj.id).aggregate(Sum('weight'))
        return baseparcel_weight['weight__sum']

    @admin.display(description=_('Стоим. посылок в $'))
    def sum_baseparcel_cost(self, obj):
        baseparcel_price = BaseParcel.objects.filter(box__flight_id=obj.id).aggregate(Sum('cost_usd'))
        return baseparcel_price['cost_usd__sum']

    @admin.display(description=_('Вес посылок'))
    def sum_parcel_weights(self, obj):
        weight = BaseParcel.objects.filter(box__flight_id=obj.id).aggregate(Sum('weight'))
        return weight['weight__sum']

    @admin.display(description=_('Вес (выдан)'))
    def sum_parcel_weights_distributed(self, obj):
        weight = BaseParcel.objects.filter(box__flight_id=obj.id, status=5).aggregate(Sum('weight'))
        return weight['weight__sum']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(status=4)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def if_change(self, obj):
        if obj.status == 5:
            obj.is_archive = True
            obj.save()
            for box in obj.box.filter(~Q(status=obj.status)):
                box.status = 5
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
        super(DeliveryAdmin, self).save_model(request, obj, form, change)
        if form.has_changed():
            self.if_change(obj)
        else:
            query_dict = request.POST

            for i in query_dict:
                if 'shelf' in i:
                    base_parcel_id = i.split('_')[-1]
                    shelf = query_dict.get(f'shelf_{base_parcel_id}')
                    if shelf:
                        base_parcel = BaseParcel.objects.get(id=int(base_parcel_id))
                        base_parcel.shelf = shelf
                        base_parcel.save()
                if 'price' in i:
                    base_parcel_id = i.split('_')[-1]
                    price = query_dict.get(f'price_{base_parcel_id}')
                    if price:
                        base_parcel = BaseParcel.objects.get(id=int(base_parcel_id))
                        base_parcel.price = price
                        base_parcel.save()
                if 'weight' in i:
                    base_parcel_id = i.split('_')[-1]
                    weight = query_dict.get(f'weight_{base_parcel_id}')
                    if weight:
                        base_parcel = BaseParcel.objects.get(id=int(base_parcel_id))
                        base_parcel.weight = weight
                        base_parcel.save()
                if 'cost_usd' in i:
                    base_parcel_id = i.split('_')[-1]
                    cost_usd = query_dict.get(f'cost_usd_{base_parcel_id}')
                    if cost_usd:
                        base_parcel = BaseParcel.objects.get(id=int(base_parcel_id))
                        base_parcel.cost_usd = cost_usd
                        base_parcel.save()
                if 'cost_kgs' in i:
                    base_parcel_id = i.split('_')[-1]
                    cost_kgs = query_dict.get(f'cost_kgs_{base_parcel_id}')
                    if cost_kgs:
                        base_parcel = BaseParcel.objects.get(id=int(base_parcel_id))
                        base_parcel.cost_kgs = cost_kgs
                        base_parcel.save()
                if 'note' in i:
                    base_parcel_id = i.split('_')[-1]
                    note = query_dict.get(f'note_{base_parcel_id}')
                    if note:
                        base_parcel = BaseParcel.objects.get(id=int(base_parcel_id))
                        base_parcel.note = note
                        base_parcel.save()

            for i in query_dict.getlist('base_parcels'):
                base_parcel = BaseParcel.objects.get(id=int(eval(i)['base_parcel']))
                base_parcel.status = int(eval(i)['status'])
                base_parcel.save()

            for i in query_dict.getlist('boxes'):
                box = Box.objects.get(id=int(eval(i)['box']))
                box.status = int(eval(i)['status'])
                box.save()
                baseparcels = BaseParcel.objects.filter(box__id=int(eval(i)['box']))
                for baseparcel in baseparcels:
                    if baseparcel.status == 5:
                        continue
                    else:
                        baseparcel.status = int(eval(i)['status'])
                        baseparcel.save()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context)


@admin.register(Archive)
class ArchiveAdmin(nested_admin.NestedModelAdmin):
    list_display = ('numeration', 'code', 'arrived_at', 'status')
    list_display_links = ('numeration', 'code', 'arrived_at', 'status')
    search_fields = ('numeration', 'box__code', 'box__base_parcel__track_code',)
    date_hierarchy = 'arrived_at'
    ordering = ('arrived_at',)
    list_filter = (('arrived_at', DateFieldListFilter), ('arrived_at', DateTimeRangeFilter))
    inlines = (ArchiveBoxNestedInline,)
    readonly_fields = ('numeration', 'code', 'arrived_at', 'status')
    fields = [readonly_fields]
    change_form_template = "admin/archive_change_form.html"

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
    list_display = (
        'get_flight', 'get_box', 'track_code', 'client_code', 'phone', 'shelf', 'price', 'weight', 'cost_usd',
        'cost_kgs', 'arrived_at',
    )
    list_display_links = ('get_flight', 'get_box', 'track_code', 'client_code', 'phone')
    readonly_fields = (
        'get_flight', 'get_box', 'track_code', 'client_code', 'phone', 'shelf', 'price', 'weight', 'cost_usd',
        'cost_kgs', 'arrived_at',
    )
    fields = [readonly_fields, 'status']
    search_fields = ('track_code',)
    date_hierarchy = 'arrived_at'
    ordering = ('arrived_at',)
    list_filter = (('arrived_at', DateFieldListFilter), ('arrived_at', DateTimeRangeFilter))
    change_form_template = "admin/unknown_change_form.html"

    def get_queryset(self, request):
        return Unknown.objects.filter(status=7)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description=_('Код рейса'))
    def get_flight(self, obj):
        flight = Flight.objects.get(box__base_parcel=obj.id)
        return flight.code

    @admin.display(description=_('Код коробки'))
    def get_box(self, obj):
        box = Box.objects.get(base_parcel=obj.id)
        return box


@admin.register(DeliveryBaseParcel)
class DeliveryBaseParcelAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        'get_flight', 'get_box', 'track_code', 'client_code', 'phone', 'shelf', 'price', 'weight', 'cost_usd',
        'cost_kgs', 'note', 'arrived_at',
    )
    list_editable = ('note',)
    list_display_links = ('get_flight', 'get_box', 'track_code', 'client_code', 'phone')
    readonly_fields = (
        'get_flight', 'get_box', 'track_code', 'client_code', 'phone', 'shelf', 'price', 'weight', 'cost_usd',
        'cost_kgs', 'arrived_at',
    )
    fields = [readonly_fields, 'status']
    search_fields = ('track_code', 'client_code', 'phone')
    date_hierarchy = 'arrived_at'
    ordering = ('arrived_at',)
    list_filter = (('arrived_at', DateFieldListFilter), ('arrived_at', DateTimeRangeFilter))
    change_form_template = "admin/unknown_change_form.html"
    actions = ('print_baseparcel', 'set_baseparcel_status')

    @admin.action(description='Распечатать')
    def print_baseparcel(self, request, queryset):
        context = {'baseparcels': queryset}
        return render(request, 'delivery_print.html', context=context)

    @admin.action(description='Изменить статус на Выдан')
    def set_baseparcel_status(self, request, queryset):
        for baseparcel in queryset:
            baseparcel.status = 5
            baseparcel.delivered_at = now()
            baseparcel.save()
            messages.info(request, f"Статус посылки {baseparcel.id} изменен на Выдан")

    def get_queryset(self, request):
        return DeliveryBaseParcel.objects.filter(box__flight__status__in=[2, 3, 4], status=4)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description=_('Код рейса'))
    def get_flight(self, obj):
        flight = Flight.objects.get(box__base_parcel=obj.id)
        return flight.code

    @admin.display(description=_('Код коробки'))
    def get_box(self, obj):
        box = Box.objects.get(base_parcel=obj.id)
        return box


class BaseParcelInline(admin.TabularInline):
    model = BaseParcel
    form = BaseParcelModelForm
    exclude = ('shelf', 'status', 'arrived_at', 'barcode', 'cost_kgs', 'note', 'delivered_at')
    template = 'admin/box_baseparcel_tabular.html'
    max_num = 500

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 50
        else:
            return 100


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
    comment = fields.Field(
        column_name='ПРИМЕЧАНИЕ',
        attribute='comment'
    )

    class Meta:
        model = Box
        import_id_fields = ['track_code']
        fields = ('created_at', 'code', 'track_code', 'weight', 'comment')


@admin.register(Box)
class BoxAdmin(ImportExportModelAdmin):
    form = BoxModelForm
    list_display = (
        'number', 'created_at', 'code', 'track_code', 'weight', 'sum_baseparcel_quantity', 'sum_baseparcel_cost',
    )
    list_display_links = ('number', 'created_at', 'code', 'track_code',)
    exclude = ('number', 'box', 'status', 'arrived_at',)
    date_hierarchy = 'created_at'
    list_filter = (('created_at', DateFieldListFilter), ('created_at', DateTimeRangeFilter),)
    search_fields = ('base_parcel__track_code',)
    resource_class = BoxAdminResource
    inlines = (BaseParcelInline,)
    change_form_template = "admin/box_change_form.html"
    save_on_top = True

    class Media:
        css = {
            'all': ('flight/box.css',)
        }

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(flight=None)

    def get_actions(self, request):
        actions = super(BoxAdmin, self).get_actions(request)
        flights = Flight.objects.filter(status=0)
        for flight in flights:
            action = make_add_box_to_flight_action(flight)
            actions[action.__name__] = (action, action.__name__, action.short_description)
        return actions

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "flight":
            kwargs["queryset"] = Flight.objects.filter(status=0)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            box = Box.objects.last()
            if not box:
                obj.number = 1
            elif box.created_at.day == now().day:
                obj.number = box.number + 1
            else:
                obj.number = 1
        super(BoxAdmin, self).save_model(request, obj, form, change)

    @admin.display(description=_('Кол. посылок'))
    def sum_baseparcel_quantity(self, obj):
        baseparcel_quantity = BaseParcel.objects.filter(box_id=obj.id).count()
        return baseparcel_quantity

    @admin.display(description=_('Стоим. посылок в $'))
    def sum_baseparcel_cost(self, obj):
        baseparcel_price = BaseParcel.objects.filter(box_id=obj.id).aggregate(Sum('cost_usd'))
        return baseparcel_price['cost_usd__sum']


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'image', 'video',)
    list_display_links = list_display


@admin.register(OrderDescription)
class OrderDescriptionAdmin(admin.ModelAdmin):
    list_display = ('description',)
    list_display_links = list_display


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('weight', 'service_type', 'air', 'truck', 'commission',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('social', 'icon',)


class AdminSiteExtension(AdminSite):
    def get_app_list(self, request):
        app_list = original_get_app_list(self, request)
        ordering = {
            "Destination": 0,
            "BaseParcel": 1,
            "Box": 2,
            "Flight": 3,
            "Arrival": 4,
            "Delivery": 5,
            'DeliveryBaseParcel': 6,
            "Unknown": 7,
            "Archive": 8,
            "Media": 9,
            'OrderDescription': 10,
            'Rate': 11,
            "Contact": 12,

        }
        for idx, app in enumerate(app_list):
            if app['app_label'] == 'flight':
                app['models'].sort(key=lambda x: ordering[x['object_name']])
                flight = app_list.pop(idx)
                app_list.insert(0, flight)
                return app_list


AdminSite.get_app_list = AdminSiteExtension.get_app_list
