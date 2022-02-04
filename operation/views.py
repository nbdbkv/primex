from rest_framework.permissions import IsAuthenticated, AllowAny
from account.models import User
from rest_framework import generics
from .models import (Parcel, Directions, Direction, ParcelInfo, DeliveryType, Envelope, Recipient, DeliveryDate, UserInfo)
from .serializers import (ParcelSerializer,
                          ParcelPaymentSerializer,
                          ParcelPaymentWithBonusSerializer,
                          DirectionsSerializer,
                          DirectionSerializer,
                          ParametersSerializer,
                          DeliveryTypeSerializer,
                          EnvelopeSerializer,
                          RecipientSerializer,
                          DeliveryDateSerializer,
                          SenderInfoSerializer
                          )

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

class DirectionView(generics.CreateAPIView):
    queryset = Direction
    serializer_class = DirectionSerializer

class ParametersView(generics.CreateAPIView):
    queryset = ParcelInfo
    serializer_class = ParametersSerializer

class DeliveryTypeView(generics.ListAPIView):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer

class EnvelopeView(generics.ListAPIView):
    queryset = Envelope.objects.all()
    serializer_class = EnvelopeSerializer

class RecipientView(generics.CreateAPIView):
    queryset = Recipient
    serializer_class = RecipientSerializer

class DeliveryDateView(generics.CreateAPIView):
    queryset = DeliveryDate
    serializer_class = DeliveryDateSerializer

class SenderView(generics.ListCreateAPIView):
    serializer_class = SenderInfoSerializer
    lookup_field = 'pk'
    def get_queryset(self):
        return User.objects.filter(pk = self.kwargs['pk'])

