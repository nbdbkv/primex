from django.shortcuts import get_list_or_404, get_object_or_404, render
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from django.views.generic import TemplateView

from operation.choices import PaymentHistoryType, PaymentTypeChoices, DirectionChoices

from operation.serializers import (
    BonusHistorySerializer,
    DeliveryStatusSerializer,
    ParcelOptionSerializer,
    DeliveryTypeSerializer,
    PackagingSerializer,
    EnvelopSerializer,
    PaymentTypeSerializer,
    CreateParcelSerializer,
    ReatriveParcelSerializer,
    PaymentHistorySerializer,
)
from operation.models import (
    DeliveryStatus,
    Distance,
    ParcelOption,
    Parcel,
    DeliveryType,
    Packaging,
    Envelop,
    PaymentHistory,
    PaymentType, ParcelDimension, ParcelPayment,
)


class PaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["parcel", "type", "payment_type"]

    def get_queryset(self):
        user = self.request.user
        queryset = PaymentHistory.objects.filter(user=user)
        return queryset


class BonusHistoryView(generics.ListAPIView):
    serializer_class = BonusHistorySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PaymentHistory.objects.filter(
            user=user, type__type=PaymentTypeChoices.BONUS
        )
        return queryset


class ParcelCreateView(generics.CreateAPIView):
    serializer_class = CreateParcelSerializer
    queryset = Parcel


class DeliveryStatusListView(generics.ListAPIView):
    serializer_class = DeliveryStatusSerializer
    queryset = DeliveryStatus.objects.all()


class ParcelOptionsListView(generics.ListAPIView):
    serializer_class = ParcelOptionSerializer
    queryset = ParcelOption.objects.all()


class DeliveryTypeListView(generics.ListAPIView):
    serializer_class = DeliveryTypeSerializer

    def get_queryset(self):
        from_dis = self.kwargs.get("from_district")
        to_dis = self.kwargs.get("to_district")
        if from_dis and to_dis:
            distance = get_object_or_404(
                Distance.objects, from_district=from_dis, to_district=to_dis
            )
            queryset = get_list_or_404(Envelop, distance=distance)
        else:
            queryset = DeliveryType.objects.all()
        return queryset


class PackagingListView(generics.ListAPIView):
    serializer_class = PackagingSerializer
    queryset = Packaging.objects.all().order_by('-id')


class EnvelopListView(generics.ListAPIView):
    serializer_class = EnvelopSerializer

    def get_queryset(self):
        from_dis = self.request.GET.get("from_district")
        to_dis = self.request.GET.get("to_district")
        if from_dis and to_dis:
            distance = get_object_or_404(
                Distance.objects, from_district=from_dis, to_district=to_dis
            )
            queryset = get_list_or_404(Envelop, distance=distance)
        else:
            queryset = Envelop.objects.all()
        return queryset


class PaymentTypeListView(generics.ListAPIView):
    serializer_class = PaymentTypeSerializer
    queryset = PaymentType.objects.all()


class ParcelListView(generics.ListAPIView):
    serializer_class = ReatriveParcelSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Parcel.objects.filter(sender=user)
        return queryset


class ParcelRetrieveView(generics.RetrieveAPIView):
    serializer_class = ReatriveParcelSerializer
    queryset = Parcel.objects.all()
    lookup_field = "code"


class PrintView(TemplateView):
    model = Parcel
    template_name = "index.html"

    def get(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        code = parcel.code
        sender = parcel.user_info.get(type=1)
        sender_place = parcel.sender.district.name
        recipient = parcel.user_info.get(type=2)
        recipient_place = Distance.objects.get(parcel=parcel).to_district.name

        fro_m = parcel.direction.get(type=DirectionChoices.FROM).district.name
        to = parcel.direction.get(type=DirectionChoices.TO).district.name

        dimension = ParcelDimension.objects.get(parcel=parcel)

        pay_status = ParcelPayment.objects.get(parcel=parcel).pay_status
        payment_type = PaymentType.objects.get(parcel=parcel).type

        context = {
            "code": code,
            "sender": sender,
            "sender_place": sender_place,
            "recipient": recipient,
            "recipient_place": recipient_place,
            "from": fro_m,
            "to": to,
            "dimension": dimension,
            "pay_status": pay_status,
            "payment_type": payment_type,
        }
        return render(request, self.template_name, context)
