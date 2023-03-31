from django.http import HttpResponse
from django.shortcuts import redirect

from flight.models import Flight, Box


def add_to_flight(request):
    print(request.POST)
    flight = request.POST.get('flights')
    boxes = request.POST.getlist('_selected_action')
    fl_obj = Flight.objects.get(id=flight)
    for b in boxes:
        box = Box.objects.get(id=int(b))
        box.flight_id = fl_obj.id
        box.save()
    return redirect('admin:flight_flight_changelist')
