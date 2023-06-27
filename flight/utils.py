import pytz
from datetime import datetime

from django.contrib import messages
from django.db.models import Sum

from core import settings

bishkek_timezone = pytz.timezone(settings.TIME_ZONE)
format_string = "%Y-%m-%d %H:%M:%S"


def make_add_box_to_flight_action(flight):
    def add_box_to_flight(modeladmin, request, queryset):
        for box in queryset:
            box.flight = flight
            box.save()
            messages.info(request, f"Коробка {box.id} добавлена в рейс {flight.code}")
    add_box_to_flight.short_description = f"Добавить в рейс {flight.code}"
    add_box_to_flight.__name__ = f"add_box_to_flight_{flight.id}"
    return add_box_to_flight


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
