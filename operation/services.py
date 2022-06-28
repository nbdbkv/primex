from decimal import Decimal

from django.db.models import Q
from django.forms import ValidationError
from decimal import Decimal

from account.models import Region, District
from operation.models import (
    Parcel,
    Envelop,
    Direction,
    ParcelDimension,
    PaymentHistory,
    PaymentType,
    PaymentDimension,
)
from operation.choices import PaymentHistoryType, PaymentTypeChoices

from uuid import uuid4
from operation.models import Parcel

def get_parcel_code_from_db():
    code = Parcel.objects.order_by('id').last().code
    code = code[-4:]
    if code == '9999':
        code = 0
    value = int(code)+1
    value = (str(value).zfill(4))
    return value


def get_parcel_code(direction: dict) -> str:
    district = direction.get("district")
    code = district.region.code + district.code
    if village := direction.get("village"):
        code += village.code
    code = str(code + get_parcel_code_from_db())
    return code


class CalculateParcelPrice:
    def __init__(self, instance: Parcel):
        self.instance = instance
        self.from_district = self.get_district_from(instance)
        self.to_district = self.get_district_to(instance)
        self.validate()

    @staticmethod
    def get_district_from(instance: Parcel) -> Region:
        district_from = instance.direction.get(type=1).district
        return district_from

    @staticmethod
    def get_district_to(instance: Parcel) -> District:
        district_to = instance.direction.get(type=2).district
        return district_to

    def validate(self):
        if Envelop.objects.filter(
            Q(distance__from_district=self.from_district)
            & Q(distance__to_district=self.to_district)
        ):
            return None
        raise ValidationError({"message": "There is no price for this area"})

    def calculate_dimension_price(self):
        parcel_dimension = self.instance.dimension

        if dimension_price_obj := Envelop.objects.filter(
            Q(distance__from_district=self.from_district)
            & Q(distance__to_district=self.to_district)
            & Q(dimension__length__gte=parcel_dimension.length)
            & Q(dimension__width__gte=parcel_dimension.width)
            & Q(dimension__height__gte=parcel_dimension.height)
        ):
            dimension_price_obj = dimension_price_obj.first()
            price = float(dimension_price_obj.price)
        else:
            dimension_price_obj = Envelop.objects.filter(
                Q(distance__from_district=self.from_district)
                & Q(distance__to_district=self.to_district)
            )
            dimension_price_obj = dimension_price_obj[2]
            price = (
                float(dimension_price_obj.price)
                + (
                    parcel_dimension.length
                    * parcel_dimension.width
                    * parcel_dimension.height
                    / 1000000
                )
                * dimension_price_obj.cube_price
            )
        dimension_weight = dimension_price_obj.dimension.weight
        if parcel_dimension.weight > dimension_weight:
            dif = parcel_dimension.weight - dimension_weight
            price += float(dimension_price_obj.kilo) * dif
        self.instance.payment.envelop = dimension_price_obj
        self.instance.save()
        return price

    def calculate_envelop_price(self):
        envelop = self.instance.payment.envelop
        price = float(envelop.price)
        return price

    def get_dimension_price(self):
        if self.instance.dimension.weight > 0  \
                or self.instance.dimension.length > 0 \
                or self.instance.dimension.height > 0:
            return self.calculate_dimension_price()
        return self.calculate_envelop_price()

    def calculate_packaging_price(self):
        packaging = self.instance.payment.packaging.all()
        price = 0
        for pack in packaging:
            price += float(pack.price) * int(pack.quantity)
        return price

    def calculate_delivery_price(self):
        delivery = self.instance.payment.delivery_type
        price = float(delivery.price)
        return price

    @property
    def price(self):
        dimension_price = self.get_dimension_price()
        packaging_price = self.calculate_packaging_price()
        delivery_price = self.calculate_delivery_price()
        price = int(dimension_price + packaging_price + delivery_price)
        return price
