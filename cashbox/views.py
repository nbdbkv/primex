from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .serializers import CashReceivingSerializer, BonusPaySerializer
from .services import Cashbox
from .permissions import IsAuth
from operation.choices import PaymentTypeChoices
from operation.models import Parcel, PaymentHistory

import hashlib


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
        data = request.data.copy()
        try:
            Parcel.objects.get(code=data["parcel_code"])
            sha1_hash = data.pop("sha1_hash")
            data["secret"] = settings.CASHBOX_SECRET
            data["amount"] = "%.2f" % float(data["amount"])
            sorted_data = [i[1] for i in sorted(data.items())]
            obj_str = "&".join(map(str, sorted_data))
            hash1 = hashlib.sha1(bytes(obj_str, "utf-8"))
            pbhash = hash1.hexdigest()
            if sha1_hash != pbhash:
                return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
            data_for_cash = {
                "code": data["parcel_code"],
                "amount": data["amount"],
            }
            cashbox = Cashbox(**data_for_cash, type=PaymentTypeChoices.OPTIMA)
            cashbox.save()
            return Response({"status": 200}, status=status.HTTP_200_OK)
        except Parcel.DoesNotExist:
            return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)

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
def check_requisite(request, *args, **kwargs):
    get_object_or_404(Parcel.objects, code=kwargs["requisite"])
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuth])
def make_payment(request, *args, **kwargs):
    data = request.data
    cashbox = Cashbox(data["requisite"], data["amount"], PaymentTypeChoices.O_PAY)
    cashbox.save()
    return Response(status=status.HTTP_202_ACCEPTED)
