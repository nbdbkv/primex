from django.shortcuts import render
from rest_framework import generics

from .models import Parcel
from .serializers import ParcelSerializer

class CreateParcelView(generics.ListCreateAPIView):
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer

class UpdateParcelView(generics.RetrieveUpdateAPIView):
    queryset = Parcel
    serializer_class = ParcelSerializer

class ListParcelView(generics.ListAPIView):
    queryset = Parcel
    serializer_class = ParcelSerializer

