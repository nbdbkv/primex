import mimetypes
import os
from wsgiref.util import FileWrapper

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from rest_framework import generics, filters, views

from flight.models import Flight, Box, BaseParcel, Media, Rate, Contact, TrackCode, OrderDescription
from flight.serializers import (
    MediaSerializer, RateSerializer, ContactSerializer, BaseParcelSerializer, OrderDescriptionSerializer,
)


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
    if not search_term:
        box = Box.objects.filter(Q(flight_id=flight) & ~Q(status=7)).distinct()
        context = {
            'qs': box,
        }
        return HttpResponse(render_to_string('my_formset2.html', context, request=request))
    else:
        baseparcels = BaseParcel.objects.filter(Q(box__flight_id=flight) & ~Q(status=7)).prefetch_related('box')
        baseparcels = baseparcels.filter(
            (Q(box__code__icontains=search_term) & ~Q(status=7)) |
            (Q(track_code__icontains=search_term) & ~Q(status=7)) |
            (Q(client_code__exact=search_term) & ~Q(status=7)) |
            (Q(phone__exact=search_term) & ~Q(status=7))
        )
        context = {
            'baseparcels': baseparcels,
        }
        return HttpResponse(render_to_string('my_formset.html', context, request=request))


def delivery_view(request):
    search_term = request.GET.get('q')
    flight = request.GET.get('flight')
    queryset = Box.objects.filter(Q(flight_id=flight) & ~Q(status=7))
    if search_term:
        queryset = queryset.filter(
            (Q(code__icontains=search_term) & ~Q(status=7)) |
            (Q(base_parcel__track_code__icontains=search_term) & ~Q(base_parcel__status=7)) |
            (Q(base_parcel__client_code__exact=search_term) & ~Q(base_parcel__status=7)) |
            (Q(base_parcel__phone__exact=search_term) & ~Q(base_parcel__status=7))
        ).distinct()
    context = {
        'qs': queryset,
    }
    html = render_to_string('delivery_formset2.html', context, request=request)
    return HttpResponse(html)


class MediaListView(generics.ListAPIView):
    serializer_class = MediaSerializer
    queryset = Media.objects.all()


class OrderDescriptionListView(generics.ListAPIView):
    serializer_class = OrderDescriptionSerializer
    queryset = OrderDescription.objects.all()


class FileDownloadListView(views.APIView):

    def get(self, request, id):
        media = Media.objects.get(id=id)
        filepath = media.video.path
        mimetype, _ = mimetypes.guess_type(filepath)
        filename = os.path.basename(media.video.name)
        filename_size = os.stat(filepath).st_size
        with open(filepath, 'rb') as file:
            content_range = 'bytes 0-{}/{}'.format(filename_size - 1, filename_size)
            response = HttpResponse(FileWrapper(file), content_type=mimetype)
            response['Content-Disposition'] = f'attachment; filename={filename}'
            response['Content-Range'] = content_range
            return response


class RateListView(generics.ListAPIView):
    serializer_class = RateSerializer
    queryset = Rate.objects.all()


class ContactListView(generics.ListAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()


class BaseParcelSearchListView(generics.ListAPIView):
    search_fields = ('track_code',)
    filter_backends = (filters.SearchFilter,)
    serializer_class = BaseParcelSerializer

    def get_queryset(self):
        user = self.request.user
        base_parcels = BaseParcel.objects.filter(Q(client_code=user.code_logistic) | Q(phone=user.phone))
        if self.request.query_params:
            return BaseParcel.objects.filter(status__in=[0, 1, 2, 3, 4]).order_by('-id')
        else:
            return base_parcels.filter(status__in=[0, 1, 2, 3, 4, 7]).order_by('-id')


class BaseParcelHistoryListView(generics.ListAPIView):
    search_fields = ('track_code',)
    filter_backends = (filters.SearchFilter,)
    serializer_class = BaseParcelSerializer

    def get_queryset(self):
        user = self.request.user
        base_parcels = BaseParcel.objects.filter(
            (Q(client_code=user.code_logistic) & Q(status__in=[5, 7])) | (Q(phone=user.phone) & Q(status__in=[5, 7]))
        )
        return base_parcels


def ajax_get_track_code_view(request):
    if not TrackCode.objects.first():
        TrackCode.objects.create()
    track_code = TrackCode.objects.first()
    track_code.code += 1
    track_code.save()
    response = {
        'code': str(track_code.code).zfill(6)
    }
    return JsonResponse(response)
