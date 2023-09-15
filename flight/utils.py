import pytz
from datetime import datetime

from django.contrib import admin, messages
from django.core.cache import cache
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from core import settings
from flight.models import BaseParcel, Box, Flight

bishkek_timezone = pytz.timezone(settings.TIME_ZONE)
format_string = "%Y-%m-%d %H:%M:%S"


def make_add_box_to_flight_action(flight):
    def add_box_to_flight(modeladmin, request, queryset):
        for box in queryset:
            box.flight = flight
            box.save()
            messages.info(request, f"Коробка {box.code} добавлена в рейс {flight.code}")
    add_box_to_flight.short_description = f"Добавить в рейс {flight.code}"
    add_box_to_flight.__name__ = f"add_box_to_flight_{flight.id}"
    return add_box_to_flight


def make_add_baseparcel_to_box_action(box):
    def add_baseparcel_to_box(modeladmin, request, queryset):
        for baseparcel in queryset:
            baseparcel.box = box
            baseparcel.save()
            messages.info(request, f"Посылка {baseparcel.track_code} добавлена в коробку {box.code}")
    add_baseparcel_to_box.short_description = f"Добавить в коробку {box.code}"
    add_baseparcel_to_box.__name__ = f"add_baseparcel_to_box_{box.id}"
    return add_baseparcel_to_box


def get_start_datetime(query_dict, start_date):
    start_time_string = query_dict.get('delivered_at__range__gte_1')
    if start_time_string:
        start_datetime_string = start_date + ' ' + start_time_string
    else:
        start_datetime_string = start_date + ' 00:00:00'
    start_datetime = datetime.strptime(start_datetime_string, format_string)
    return bishkek_timezone.localize(start_datetime)


def get_end_datetime(query_dict, end_date):
    end_time_string = query_dict.get('delivered_at__range__lte_1')
    if end_time_string:
        end_datetime_string = end_date + ' ' + end_time_string
    else:
        end_datetime_string = end_date + ' 00:00:00'
    end_datetime = datetime.strptime(end_datetime_string, format_string)
    return bishkek_timezone.localize(end_datetime)


def get_extra_context(baseparcels):
    total_quantity = baseparcels.count()
    total_weight = baseparcels.aggregate(Sum('weight'))
    total_cost_kgs = baseparcels.aggregate(Sum('cost_kgs'))
    extra_context = {
        'total_quantity': total_quantity,
        'total_weight': total_weight['weight__sum'],
        'total_cost_kgs': total_cost_kgs['cost_kgs__sum']
    }
    return extra_context


def get_field(field_str, i, query_dict):
    base_parcel_id = i.split('_')[-1]
    field = query_dict.get(f'{field_str}_{base_parcel_id}')
    if field:
        base_parcel = BaseParcel.objects.get(id=int(base_parcel_id))
        match field_str:
            case 'shelf':
                base_parcel.shelf = field
            case 'price':
                base_parcel.price = field
            case 'weight':
                base_parcel.weight = field
            case 'cost_usd':
                base_parcel.cost_usd = field
            case 'cost_kgs':
                base_parcel.cost_kgs = field
            case 'note':
                base_parcel.note = field
        base_parcel.save()


class FieldSum:
    @admin.display(description=_('Кол. коробок'))
    def sum_box_quantity(self, obj):
        key = str(obj) + '_' + 'box_quantity'
        if key in cache:
            box_quantity = cache.get(key)
        else:
            box_quantity = Box.objects.filter(flight_id=obj.id).count()
            cache.set(key, box_quantity, timeout=480)
        return box_quantity

    @admin.display(description=_('Вес коробок'))
    def sum_box_weight(self, obj):
        key = str(obj) + '_' + 'box_weight'
        if key in cache:
            box_weight = {'weight__sum': cache.get(key)}
        else:
            box_weight = Box.objects.filter(flight_id=obj.id).aggregate(Sum('weight'))
            cache.set(key, box_weight['weight__sum'], timeout=420)
        return box_weight['weight__sum']

    @admin.display(description=_('Кол. посылок'))
    def sum_baseparcel_quantity(self, obj):
        key = str(obj) + '_' + 'baseparcel_quantity'
        if key in cache:
            baseparcel_quantity = cache.get(key)
        else:
            baseparcel_quantity = BaseParcel.objects.filter(box_id=obj.id).count()
            cache.set(key, baseparcel_quantity, timeout=360)
        return baseparcel_quantity

    @admin.display(description=_('Вес посылок'))
    def sum_baseparcel_weight(self, obj):
        key = str(obj) + '_' + 'baseparcel_weight'
        if key in cache:
            baseparcel_weight = {'weight__sum': cache.get(key)}
        else:
            baseparcel_weight = BaseParcel.objects.filter(box__flight_id=obj.id).aggregate(Sum('weight'))
            cache.set(key, baseparcel_weight['weight__sum'], timeout=540)
        return baseparcel_weight['weight__sum']

    @admin.display(description=_('Стоим. посылок в $'))
    def sum_baseparcel_cost(self, obj):
        key = str(obj) + '_' + 'baseparcel_cost'
        if key in cache:
            baseparcel_cost = {'cost_usd__sum': cache.get(key)}
        else:
            baseparcel_cost = BaseParcel.objects.filter(box__flight_id=obj.id).aggregate(Sum('cost_usd'))
            cache.set(key, baseparcel_cost['cost_usd__sum'], timeout=600)
        return baseparcel_cost['cost_usd__sum']

    @admin.display(description=_('Стоим. посылок в $'))
    def sum_box_baseparcel_cost(self, obj):
        key = str(obj) + '_' + 'box_baseparcel_cost'
        if key in cache:
            box_baseparcel_cost = {'cost_usd__sum': cache.get(key)}
        else:
            box_baseparcel_cost = BaseParcel.objects.filter(box_id=obj.id).aggregate(Sum('cost_usd'))
            cache.set(key, box_baseparcel_cost['cost_usd__sum'], timeout=300)
        return box_baseparcel_cost['cost_usd__sum']

    @admin.display(description=_('Вес (выдан)'))
    def sum_baseparcel_weight_distributed(self, obj):
        key = str(obj) + '_' + 'baseparcel_weight_distributed'
        if key in cache:
            baseparcel_weight_distributed = {'weight__sum': cache.get(key)}
        else:
            baseparcel_weight_distributed = BaseParcel.objects.filter(
                box__flight_id=obj.id, status=5
            ).aggregate(Sum('weight'))
            cache.set(key, baseparcel_weight_distributed['weight__sum'], timeout=300)
        return baseparcel_weight_distributed['weight__sum']

    @admin.display(description=_('Код рейса'))
    def get_flight(self, obj):
        if obj in cache:
            flight_code = cache.get(obj)
        else:
            flight = Flight.objects.get(box__base_parcel=obj.id)
            flight_code = flight.code
            cache.set(obj, flight_code, timeout=6000)
        return flight_code
