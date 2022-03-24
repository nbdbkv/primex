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
    Town
)
from operation.choices import PaymentHistoryType, PaymentTypeChoices

from uuid import uuid4


def get_parcel_code(direction: dict) -> str:
    district = direction.get("district")
    code = district.region.code + district.code
    if village := direction.get("village"):
        code += village.code
    code = str(code + str(uuid4()).replace("-", ""))[:15]
    return code


class CalculateParcelPrice:
    def __init__(self, instance: Parcel, envelop):
        self.instance = instance
        self.from_region = self.get_region_from(instance)
        self.to_district = self.get_district_to(instance)
        self.envelop = envelop

    @staticmethod
    def get_region_from(instance: Parcel) -> Region:
        region_from = instance.direction.get(type=1).district.region
        return region_from

    @staticmethod
    def get_district_to(instance: Parcel) -> District:
        district_to = instance.direction.get(type=2).district
        return district_to

    def calculate_dimension_cube(self, parcel_dimension):
        test = 0
        towns = Town.objects.all()
        print(self.to_district.name)
        for town in towns:
            if town.name == self.to_district.name:
                test = 1
        if test:
            cube = ((parcel_dimension.length * parcel_dimension.width * parcel_dimension.height) / 1000000)
            price = (cube * 1000)
        else:
            cube = ((parcel_dimension.length * parcel_dimension.width * parcel_dimension.height) / 1000000)
            price = (cube * 1500)
        return price

    def calculate_dimension_price(self):
        parcel_dimension = self.instance.dimension
        dimension = self.envelop.dimension.filter().first()
        test = 0
        price = 0
        if dimension.length >= parcel_dimension.length and \
                dimension.width >= parcel_dimension.width and \
                dimension.height >= parcel_dimension.height:
            test = 1

        elif not test:
            dimension = self.envelop.dimension.filter().last()

        if not test and (dimension.length >= parcel_dimension.length and \
                dimension.width >= parcel_dimension.width and \
                dimension.height >= parcel_dimension.height):
            dimension = self.envelop.dimension.filter().last()
        elif not test and (dimension.length <= parcel_dimension.length or \
                    dimension.width <= parcel_dimension.width or \
                    dimension.height <= parcel_dimension.height):
            price = self.calculate_dimension_cube(parcel_dimension)
        price += float(dimension.price)
        dimension_weight = dimension.weight

        if parcel_dimension.weight > dimension_weight:
            dif = parcel_dimension.weight - dimension_weight
            price += float(self.envelop.kilo) * dif

        self.instance.payment.envelop = self.envelop
        self.instance.save()
        return price

    def calculate_envelop_price(self):
        envelop = self.instance.payment.envelop
        price = float(envelop.price)
        return price

    def get_dimension_price(self):
        if self.instance.dimension:
            try:
                return self.calculate_dimension_price()
            except KeyError:
                raise ValidationError({"message": "There is no price for this area"})
        else:
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
        envelope_price = self.calculate_envelop_price()
        price = int(dimension_price + packaging_price + delivery_price + envelope_price)
        bonus = price * 0.05

        PaymentHistory.objects.create(
            user=self.instance.sender,
            parcel=self.instance,
            type=PaymentType.objects.get(type=PaymentTypeChoices.BONUS),
            sum=bonus,
            payment_type=PaymentHistoryType.DEBIT,
        )
        self.instance.sender.points += Decimal(bonus)
        self.instance.sender.save()
        return price
