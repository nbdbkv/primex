from django.contrib import messages


def make_add_box_to_flight_action(flight):
    def add_box_to_flight(modeladmin, request, queryset):
        for box in queryset:
            box.flight = flight
            box.save()
            messages.info(request, "Коробка {0} добавлена в рейс {1}".format(box.id, flight.numeration))
    add_box_to_flight.short_description = "Добавить в рейс {0}".format(flight.numeration)
    add_box_to_flight.__name__ = 'add_box_to_flight_{0}'.format(flight.id)
    return add_box_to_flight
