from django.shortcuts import render
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
    ParcelOption,
    Parcel,
    DeliveryType,
    Packaging,
    Envelop,
    PaymentHistory,
    PaymentType,
)
from operation.filters import EnvelopFilter


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
    queryset = DeliveryType.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["distance__from_region", "distance__to_district"]


class PackagingListView(generics.ListAPIView):
    serializer_class = PackagingSerializer
    queryset = Packaging.objects.all()


class EnvelopListView(generics.ListAPIView):
    serializer_class = EnvelopSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EnvelopFilter

    def get_queryset(self, *args, **kwargs):

        return Envelop.objects.filter()


class PaymentTypeListView(generics.ListAPIView):
    serializer_class = PaymentTypeSerializer
    queryset = PaymentType.objects.all()


class ParcelListView(generics.ListAPIView):
    serializer_class = ReatriveParcelSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)
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
        sender = parcel.user_info.get(type=1)
        recipient = parcel.user_info.get(type=2)

        fro_m = parcel.direction.get(type=DirectionChoices.FROM).district.name
        to = parcel.direction.get(type=DirectionChoices.TO).district.name

        context = {
            "data": parcel,
            "sender": sender,
            "recipient": recipient,
            "from": fro_m,
            "to": to,
        }
        return render(request, self.template_name, context)
