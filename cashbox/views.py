from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import CashReceivingSerializer
from .services import Cashbox
from operation.choices import PaymentTypeChoices
from operation.models import PaymentHistory


class PaymentViewSet(viewsets.GenericViewSet):
    serializer_class = CashReceivingSerializer
    queryset = PaymentHistory.objects

    def get_valid_data(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = {
            "code": serializer.data["parcel_code"],
            "amount": serializer.data["amount"],
        }
        return data

    @action(["post"], detail=False)
    def optima(self, request, *args, **kwargs):
        data = self.get_valid_data(request.data)
        cashbox = Cashbox(**data, type=PaymentTypeChoices.OPTIMA)
        cashbox.save()
        return Response(status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def m_bank(self, request, *args, **kwargs):
        data = self.get_valid_data(request.data)
        cashbox = Cashbox(**data, type=PaymentTypeChoices.MBANK)
        cashbox.save()
        return Response(status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def megapay(self, request, *args, **kwargs):
        data = self.get_valid_data(request.data)
        cashbox = Cashbox(**data, type=PaymentTypeChoices.MEGAPAY)
        cashbox.save()
        return Response(status=status.HTTP_200_OK)
