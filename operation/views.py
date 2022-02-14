from rest_framework import generics
from operation.serializers import CreateParcelSerializer
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

# class GetParcelInfoView(generics.RetrieveAPIView):
#     serializer_class = GetParcelInfoSerializer
#
#     def get_queryset(self, *args, **kwargs):
#         return Parcel.objects.get(pk=kwargs['pk'])

