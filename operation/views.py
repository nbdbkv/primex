from rest_framework import generics
from operation.serializers import (
    CreateParcelSerializer,
    DeliveryStatusSerializer,
    ParcelOptionSerializer,
    DeliveryTypeSerializer,
    PackagingSerializer,
    PaymentTypeSerializer,
    PriceListSerializer,
    PriceEnvelopSerializer,
    RetrieveParcelSerializer,
)

from operation.models import (
    DeliveryStatus,
    ParcelOption,
    Parcel,
    DeliveryType,
    Packaging,
    PayStatus,
    PriceList,
    Envelop,
    PriceEnvelop,
    PaymentDimension,
    DimensionPrice,
    ParcelPayment,
    PaymentType,
    Payment,
    Direction,
    UserInfo,
    ParcelDimension
)


class ParcelCreateView(generics.CreateAPIView):
    serializer_class = CreateParcelSerializer
    queryset = Parcel
    

class ParcelOptionsListView(generics.ListAPIView):
    serializer_class = ParcelOptionSerializer
    queryset = ParcelOption.objects.all()


class DeliveryStatusListView(generics.ListAPIView):
    serializer_class = DeliveryStatusSerializer
    queryset = DeliveryStatus.objects.all()


class DeliveryTypeListView(generics.ListAPIView):
    serializer_class = DeliveryTypeSerializer
    queryset = DeliveryType.objects.all()
    

class PackagingListView(generics.ListAPIView):
    serializer_class = PackagingSerializer
    queryset = Packaging.objects.all()
    

class PriceListView(generics.ListAPIView):
    serializer_class = PriceListSerializer
    queryset = PriceList.objects.all()


class PaymentTypeListView(generics.ListAPIView):
    serializer_class = PaymentTypeSerializer
    queryset = PaymentType.objects.all()
    

class PriceEnvelopListView(generics.ListAPIView):
    serializer_class = PriceEnvelopSerializer
    queryset = PriceEnvelop.objects.all()


class ParcelListView(generics.ListAPIView):
    serializer_class = RetrieveParcelSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Parcel.objects.filter(sender=user)
        return queryset


class ParcelRetrieveView(generics.RetrieveAPIView):
    serializer_class = RetrieveParcelSerializer
    queryset = Parcel.objects.all()
