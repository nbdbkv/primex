from rest_framework.permissions import IsAuthenticated, AllowAny
from account.models import User
from rest_framework import generics
from .models import (Parcel, Directions, Direction, ParcelInfo, DeliveryType, Envelope, Recipient, ParcelDate, UserInfo, Town, Area, Package)
from .serializers import (
                          TownSeralizer,
                          AreaSerializer,
                          ParcelSerializer,
                          ParcelPaymentSerializer,
                          ParcelPaymentWithBonusSerializer,
                          DirectionsSerializer,
                          DirectionSerializer,
                          ParametersSerializer,
                          DeliveryTypeSerializer,
                          EnvelopeSerializer,
                          RecipientSerializer,

                          ParcelDateSerializer,
                          SenderInfoSerializer,
                          PackageTypeSerializer,
                          ParcelStatusSerializer,
                          GetDataSerializer,
                          )

class TownsView(generics.ListAPIView):
    queryset = Town.objects.all()
    serializer_class = TownSeralizer

class AreasView(generics.ListAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class CreateParcelView(generics.CreateAPIView):
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer

    # def perform_create(self, serializer):
    #     serializer.save(price=100)

class UpdateParcelView(generics.RetrieveUpdateAPIView):
    queryset = Parcel
    serializer_class = ParcelSerializer

class ListParcelView(generics.ListAPIView):
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer

class PaymentParcelView(generics.RetrieveAPIView):
    queryset = Parcel
    serializer_class = ParcelPaymentSerializer

class PaymentParcelWithBonusView(generics.RetrieveAPIView):
    queryset = Parcel
    serializer_class = ParcelPaymentWithBonusSerializer

class DirectionsView(generics.CreateAPIView):
    queryset = Directions
    serializer_class = DirectionsSerializer

class DirectionView(generics.ListCreateAPIView):
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer

class ParametersView(generics.CreateAPIView):
    queryset = ParcelInfo
    serializer_class = ParametersSerializer

class DeliveryTypeView(generics.ListCreateAPIView):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer

class PackageTypeView(generics.ListAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageTypeSerializer


class EnvelopeView(generics.ListAPIView):
    queryset = Envelope.objects.all()
    serializer_class = EnvelopeSerializer

class RecipientView(generics.CreateAPIView):
    queryset = Recipient
    serializer_class = RecipientSerializer

class ParcelDateView(generics.CreateAPIView):
    queryset = ParcelDate
    serializer_class = ParcelDateSerializer

class ParcelStatusView(generics.RetrieveAPIView):
    serializer_class = ParcelStatusSerializer
    lookup_field = 'pk'
    def get_queryset(self):
        return  Parcel.objects.filter(pk=self.kwargs.get('pk'))

class SenderView(generics.ListCreateAPIView):
    serializer_class = SenderInfoSerializer
    lookup_field = 'pk'
    def get_queryset(self):
        return User.objects.filter(pk = self.kwargs['pk'])

class GetDataView(generics.RetrieveAPIView):
    serializer_class = GetDataSerializer
    lookup_field = 'pk'
    def get_queryset(self):
        return Parcel.objects.filter(pk=self.kwargs['pk'])
