from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .serializers import CashReceivingSerializer, BonusPaySerializer
from .services import Cashbox
from .permissions import IsAuth
from operation.choices import PaymentTypeChoices
from operation.models import Parcel, PaymentHistory


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

    def get_serializer_class(self):
        if self.action == "bonus":
            return BonusPaySerializer
        return super().get_serializer_class()

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

    @action(["post"], detail=False)
    def bonus(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.make_payment()
        return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuth])
def check_requisite(request, *args, **kwargs):
    if Parcel.objects.filter(code=kwargs["requisite"]).exists():
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuth])
def make_payment(request, *args, **kwargs):
    data = request.data
    cashbox = Cashbox(data["requisite"], data["amount"], PaymentTypeChoices.O_PAY)
    cashbox.save()
    return Response(status=status.HTTP_202_ACCEPTED)
