import mimetypes
import os
from wsgiref.util import FileWrapper

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from rest_framework import generics, filters, views

from flight.models import Flight, Box, BaseParcel, Media, Rate, Contact, TrackCode
from flight.serializers import MediaSerializer, RateSerializer, ContactSerializer, BaseParcelSerializer


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
            (Q(base_parcel__track_code__icontains=search_term) & ~Q(base_parcel__status=7)) |
            (Q(base_parcel__client_code__exact=search_term) & ~Q(base_parcel__status=7))
        ).distinct()
    context = {
        'qs': queryset,
    }
    html = render_to_string('my_formset2.html', context, request=request)
    return HttpResponse(html)


class MediaListView(generics.ListAPIView):
    serializer_class = MediaSerializer
    queryset = Media.objects.all()


class DeliveryPrintView(TemplateView):
    template_name = 'delivery_print.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if 'q' in request.session:
            q = request.session['q']
            context['baseparcels'] = BaseParcel.objects.filter(Q(track_code=q) | Q(client_code=q))
            del request.session['q']
        return self.render_to_response(context)


class FileDownloadListView(views.APIView):

    def get(self, request, id):
        media = Media.objects.get(id=id)
        filepath = media.video.path
        mimetype, _ = mimetypes.guess_type(filepath)
        filename = os.path.basename(media.video.name)
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
    search_fields = ('track_code',)
    filter_backends = (filters.SearchFilter,)
    serializer_class = BaseParcelSerializer

    def get_queryset(self):
        user = self.request.user
        base_parcels = BaseParcel.objects.filter(Q(client_code=user.code_logistic) | Q(phone=user.phone))
        if self.request.query_params:
            return base_parcels.filter(status__in=[0, 1, 2, 3, 4, 5, 7]).order_by('-id')
        else:
            return base_parcels.filter(status__in=[0, 1, 2, 3, 4, 7]).order_by('-id')


class BaseParcelHistoryListView(generics.ListAPIView):
    search_fields = ('track_code',)
    filter_backends = (filters.SearchFilter,)
    serializer_class = BaseParcelSerializer

    def get_queryset(self):
        user = self.request.user
        base_parcels = BaseParcel.objects.filter(
            (Q(client_code=user.code_logistic) & Q(status=5)) | (Q(phone=user.phone) & Q(status=5))
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
