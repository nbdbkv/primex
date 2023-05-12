import mimetypes
from wsgiref.util import FileWrapper

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string

from rest_framework import generics, filters

from core.settings import BASE_DIR
from flight.models import Flight, Box, BaseParcel, Media, Rate, Contact
from flight.serializers import MediaSerializer, RateSerializer, ContactSerializer, BaseParcelSearchSerializer


def add_to_flight(request):
    flight = request.POST.get('flights')
    boxes = request.POST.getlist('_selected_action')
    fl_obj = Flight.objects.get(id=int(flight))
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


def my_view(request):
    search_term = request.GET.get('q')
    flight = request.GET.get('flight')
    queryset = Box.objects.filter(Q(flight_id=flight) & ~Q(status=7))
    if search_term:
        queryset = queryset.filter(
            (Q(code__icontains=search_term) & ~Q(status=7)) |
            (Q(base_parcel__code__icontains=search_term) & ~Q(base_parcel__status=7)) |
            (Q(base_parcel__client_code__exact=search_term) & ~Q(base_parcel__status=7))
        )
    context = {
        'qs': queryset,
    }
    html = render_to_string('my_formset2.html', context, request=request)
    return HttpResponse(html)


class MediaListView(generics.ListAPIView):
    serializer_class = MediaSerializer
    queryset = Media.objects.all()


class FileDownloadListView(generics.ListAPIView):

    def get(self, request, filename):
        filepath = str(BASE_DIR) + '/media/operation/media/video/' + filename
        mimetype, _ = mimetypes.guess_type(filepath)
        with open(filepath, 'rb') as file:
            response = HttpResponse(FileWrapper(file), content_type=mimetype)
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response


class RateListView(generics.ListAPIView):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()


class ContactListView(generics.ListAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()


class BaseParcelSearchListView(generics.ListAPIView):
    search_fields = ('code', 'client_code',)
    filter_backends = (filters.SearchFilter,)
    serializer_class = BaseParcelSearchSerializer

    def get_queryset(self):
        if self.request.query_params:
            return BaseParcel.objects.filter(status__in=[0, 1, 2, 3, 4])
        else:
            user = self.request.user
            return BaseParcel.objects.filter(client_code=user.code_logistic, status__in=[0, 1, 2, 3, 4])
