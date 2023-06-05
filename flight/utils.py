from django.contrib import messages


def make_add_box_to_flight_action(flight):
    def add_box_to_flight(modeladmin, request, queryset):
        for box in queryset:
            box.flight = flight
            box.save()
            messages.info(request, f"Коробка {box.id} добавлена в рейс {flight.code}")
    add_box_to_flight.short_description = f"Добавить в рейс {flight.numeration}{flight.code}"
    add_box_to_flight.__name__ = f"add_box_to_flight_{flight.id}"
    return add_box_to_flight
