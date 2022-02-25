from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from operation.serializers import (
    DeliveryStatusSerializer,
    ParcelOptionSerializer,
    DeliveryTypeSerializer,
    PackagingSerializer,
    EnvelopSerializer,
    PaymentTypeSerializer,
    CreateParcelSerializer,
    GetUserBonusSerializer
)
from operation.models import (
    DeliveryStatus,
    ParcelOption,
    Parcel,
    DeliveryType,
    Packaging,
    Envelop,
    PaymentType
)


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
    

class PackagingListView(generics.ListAPIView):
    serializer_class = PackagingSerializer
    queryset = Packaging.objects.all()
    

class EnvelopListView(generics.ListAPIView):
    serializer_class = EnvelopSerializer
    queryset = Envelop.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['distance__from_region', 'distance__to_district']


class PaymentTypeListView(generics.ListAPIView):
    serializer_class = PaymentTypeSerializer
    queryset = PaymentType.objects.all()

class GetUserBonusView(generics.RetrieveAPIView):
    serializer_class = GetUserBonusSerializer
    lookup_field = 'pk'
    queryset = Parcel

# class ParcelListView(generics.ListAPIView):
#     serializer_class = RetrieveParcelSerializer
    
#     def get_queryset(self):
#         user = self.request.user
#         queryset = Parcel.objects.filter(sender=user)
#         return queryset


# class ParcelRetrieveView(generics.RetrieveAPIView):
#     serializer_class = RetrieveParcelSerializer
#     queryset = Parcel.objects.all()
