from decimal import Decimal

from django.db.models import Q
from django.forms import ValidationError
from decimal import Decimal

from account.models import Region, District
from operation.models import Parcel, Envelop, Direction, ParcelDimension, PaymentHistory, PaymentType, PaymentDimension
from operation.choices import PaymentHistoryType, PaymentTypeChoices

from uuid import uuid4


def get_parcel_code(direction: dict) -> str:
    district = direction.get('district')
    code = district.region.code + district.code
    if village := direction.get('village'):
        code += village.code
    code = str(code + str(uuid4()).replace('-', ''))[:15]
    return code


class CalculateParcelPrice:
    def __init__(self, instance: Parcel):
        self.instance = instance
        self.from_region = self.get_region_from(instance)
        self.to_district = self.get_district_to(instance)
        self.test = 0

    @staticmethod
    def get_region_from(instance: Parcel) -> Region:
        region_from = instance.direction.get(type=1).district.region
        return region_from

    @staticmethod
    def get_district_to(instance: Parcel) -> District:
        district_to = instance.direction.get(type=2).district
        return district_to

    def calculate_dimension(self, parcel_dimension):
        cube = ((parcel_dimension.length * parcel_dimension.width * parcel_dimension.height) / 1000000)
        price = (cube * 1500)
        if self.to_district.name == 'Ош' or self.to_district.name == 'Жалал Абад':
            cube = ((parcel_dimension.length * parcel_dimension.width * parcel_dimension.height) / 1000000)
            price = (cube * 1000)

        return price

    def check(self, x):
        price = 0
        print(self.to_district.name == 'Ош')
        if x == 1:
            if self.to_district.name == 'Ош' or self.to_district.name == 'Жалал Абад':
                price = 200
                self.test = 1
        if x == 2:
            if self.to_district.name == 'Ош' or self.to_district.name == 'Жалал Абад':
                price = 250
                self.test = 1
        return price

    def calculate_dimension_price(self):
        parcel_dimension = self.instance.dimension
        self.check(2)
        if parcel_dimension.length <= 20 and parcel_dimension.width <= 20 and parcel_dimension.height <= 20:
            dimension_price_obj = PaymentDimension.objects.get(pk=1)
            price = self.check(1)

        elif parcel_dimension.length > 20 and parcel_dimension.length <= 30 and \
                parcel_dimension.width > 20 and parcel_dimension.width <= 30 and \
                parcel_dimension.height <= 20:
            dimension_price_obj = PaymentDimension.objects.get(pk=2)
            price = self.check(2)
        else:
            dimension_price_obj = PaymentDimension.objects.get(pk=2)
            price = float(dimension_price_obj.price)
            if self.test:
                price = self.check(2)
            print(self.calculate_dimension(parcel_dimension))
            price += self.calculate_dimension(parcel_dimension)
        if not (price):
            price = float(dimension_price_obj.price)

        dimension_weight = dimension_price_obj.weight
        if parcel_dimension.weight > dimension_weight:
            dif = parcel_dimension.weight - dimension_weight
            price += float(12) * dif
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
                raise ValidationError({'message': 'There is no price for this area'})
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
        envelop_price = self.calculate_envelop_price()
        price = int(dimension_price + packaging_price + delivery_price + envelop_price)
        bonus = price * 0.05

        PaymentHistory.objects.create(
            user=self.instance.sender,
            parcel=self.instance,
            type=PaymentType.objects.get(type=PaymentTypeChoices.BONUS),
            sum=bonus,
            payment_type=PaymentHistoryType.DEBIT
        )
        self.instance.sender.points += Decimal(bonus)
        self.instance.sender.save()
        return price
