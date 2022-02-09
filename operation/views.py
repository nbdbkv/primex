from rest_framework import generics
from rest_framework.response import Response
from operation.serializers import (
    CreateParcelSerializer,
    ListParcelSerializer,
)

from operation.models import (
    Parcel,
    User,
    DeliveryType,
    DeliveryStatus,
    UserInfo,
    ParcelDimension,
    Direction,
)
class CreateParcelInfoView(generics.CreateAPIView):
    serializer_class =  CreateParcelSerializer
    queryset = Parcel
    depth = 2

    def create(self, request, *args, **kwargs):
        parcel_data = request.data
        print(request.data)
        new_parcel = Parcel.objects.create(
            titl=Parcel.objects.get(title=parcel_data['title']),
            description=Parcel.objects.get(discriiption=parcel_data['desctoption']),
            code=Parcel.objects.get(code=parcel_data['code']),
            sending_date=Parcel.objects.get(sendint_date=parcel_data['sending_date']),
            sender = User.objects.get(id=parcel_data['sender']),
            status = Parcel.objects.get(status=parcel_data['status']),
        )
        new_parcel.save()
        serializer = CreateParcelSerializer(new_parcel)
        return Response(serializer.data)

class ListParcelInfoView(generics.ListAPIView):
    serializer_class = ListParcelSerializer
    queryset = Parcel.objects.all()




