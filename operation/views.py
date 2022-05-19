from django.shortcuts import get_list_or_404, get_object_or_404, render
from rest_framework import generics, status
from django_filters.rest_framework import DjangoFilterBackend
from django.views.generic import TemplateView
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from operation.choices import (
    PaymentHistoryType,
    PaymentTypeChoices,
    DirectionChoices,
    PayStatusChoices,
    PayStatusChoicesRu
)
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
    ImageSerializer,
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
    PaymentType,
    ParcelDimension,
    ParcelPayment,
    Direction,
    Payment,
    Images
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
        queryset = get_list_or_404(
            PaymentHistory.objects.filter(type__type=PaymentTypeChoices.BONUS),
            user=user,
        )
        return queryset


class ParcelCreateView(generics.CreateAPIView):
    serializer_class = CreateParcelSerializer
    queryset = Parcel


class ParcelImageCreateView(generics.CreateAPIView):
    serializer_class = ImageSerializer
    queryset = Images

    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist('img', None)
        _serializer = self.serializer_class(data=request.data, context={'images': images})
        if _serializer.is_valid():
            _serializer.save()
            return Response(data=_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    queryset = Packaging.objects.all().order_by("-id")


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
        sender_place = parcel.direction.get(type=DirectionChoices.FROM).destination
        recipient = parcel.user_info.get(type=2)
        recipient_place = parcel.direction.get(type=DirectionChoices.TO).destination
        fro_m = parcel.direction.get(type=DirectionChoices.FROM).district.name
        to = parcel.direction.get(type=DirectionChoices.TO).district.name

        parcel_payment = ParcelPayment.objects.get(parcel=parcel)
        payments = Payment.objects.filter(parcel=parcel_payment)
        payment_types = [payment.type for payment in payments]
        payment_id = Payment.objects.filter(parcel=parcel_payment).first().id
        payment = Payment.objects.get(pk=payment_id)
        pay_status = payment.parcel.pay_status

        if pay_status == PayStatusChoices.IN_ANTICIPATION:
            pay_status = PayStatusChoicesRu.IN_ANTICIPATION
        else:
            pay_status = PayStatusChoicesRu.PAID
        context = {
            "code": code,
            "sender": sender,
            "sender_place": sender_place,
            "recipient": recipient,
            "recipient_place": recipient_place,
            "from": fro_m,
            "to": to,
            "payment_types": payment_types,
            "pay_status": pay_status,
        }
        return render(request, self.template_name, context)
