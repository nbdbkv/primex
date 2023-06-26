from datetime import datetime

from django.contrib import messages
from django.db.models import Sum


def make_add_box_to_flight_action(flight):
    def add_box_to_flight(modeladmin, request, queryset):
        for box in queryset:
            box.flight = flight
            box.save()
            messages.info(request, f"Коробка {box.id} добавлена в рейс {flight.code}")
    add_box_to_flight.short_description = f"Добавить в рейс {flight.code}"
    add_box_to_flight.__name__ = f"add_box_to_flight_{flight.id}"
    return add_box_to_flight


def get_start_datetime(query_dict):
    if query_dict.get('delivered_at__range__gte_1'):
        start_date_string = query_dict.get('delivered_at__range__gte_0')
        start_time_string = query_dict.get('delivered_at__range__gte_1')
        start_datetime_string = start_date_string + ' ' + start_time_string
        format_string = "%Y-%m-%d %H:%M:%S"
        return datetime.strptime(start_datetime_string, format_string)


def get_end_datetime(query_dict):
    if query_dict.get('delivered_at__range__lte_1'):
        end_date_string = query_dict.get('delivered_at__range__lte_0')
        end_time_string = query_dict.get('delivered_at__range__lte_1')
        end_datetime_string = end_date_string + ' ' + end_time_string
        format_string = "%Y-%m-%d %H:%M:%S"
        return datetime.strptime(end_datetime_string, format_string)


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
