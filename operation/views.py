from rest_framework import generics
from rest_framework.response import Response
from operation.serializers import (
    CreateParcelInfoSerializer,
    ListParcelInfoSerializer,
)

from operation.models import (
    Parcel,
    User,
    DeliveryType,
    DeliveryStatus,
    ParcelInfo,
    UserInfo,
    ParcelDimension,
    ParcelOptions,
    Direction,
)
class CreateParcelInfoView(generics.CreateAPIView):
    serializer_class =  CreateParcelInfoSerializer
    queryset = ParcelInfo

    def create(self, request, *args, **kwargs):
        parcel_data = request.data
        print(request.data)
        new_parcel = ParcelInfo.objects.create(
            parcel=Parcel.objects.get(id=parcel_data['parcel']),
            sender_info=UserInfo.objects.get(id=parcel_data['sender_info']),
            recipient_info=UserInfo.objects.get(id=parcel_data['recipient_info']),
            dimension=ParcelDimension.objects.get(id=parcel_data['dimension']),
            options = ParcelOptions.objects.get(id=parcel_data['options']),
            location_from=Direction.objects.get(id=parcel_data['location_from']),
            location_to=Direction.objects.get(id=parcel_data['location_to']),
        )
        new_parcel.save()
        serializer = CreateParcelInfoSerializer(new_parcel)
        return Response(serializer.data)

class ListParcelInfoView(generics.ListAPIView):
    serializer_class = ListParcelInfoSerializer
    queryset = ParcelInfo.objects.all()




