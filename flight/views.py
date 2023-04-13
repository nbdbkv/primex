from django.shortcuts import redirect

from flight.models import Flight, Box, BaseParcel


def add_to_flight(request):
    flight = request.POST.get('flights')
    boxes = request.POST.getlist('_selected_action')
    fl_obj = Flight.objects.get(id=flight)
    for b in boxes:
        box = Box.objects.get(id=int(b))
        box.flight_id = fl_obj.id
        box.save()
    return redirect('admin:flight_flight_changelist')


def add_to_box(request):
    box = request.POST.get('boxes')
    parcels = request.POST.getlist('_selected_action')
    bx_obj = Box.objects.get(id=int(box))
    for p in parcels:
        parcel = BaseParcel.objects.get(id=int(p))
        parcel.box_id = bx_obj.id
        parcel.save()
    return redirect('admin:flight_box_changelist')


from django.http import HttpResponse
from django.template.loader import render_to_string
from flight.models import Box


def my_view(request):
    search_term = request.GET.get('q')
    flight = request.GET.get('flight')
    queryset = Box.objects.filter(flight_id=flight)
    if search_term:
        queryset = queryset.filter(code__icontains=search_term)
    all = Box.objects.filter(flight_id=flight)
    context = {
        'qs': queryset,
        'all': all
    }
    html = render_to_string('my_formset2.html', context, request=request)
    return HttpResponse(html)
