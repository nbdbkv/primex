from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from rest_framework import generics
from .models import Parcel
from .serializers import (ParcelSerializer,
                          ParcelPaymentSerializer,
                          ParcelPaymentWithBonusSerializer,)

class CreateParcelView(generics.CreateAPIView):
    queryset = Parcel
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


