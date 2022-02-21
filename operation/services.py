from django.db.models import Q
from django.forms import ValidationError

from account.models import Region, District
from operation.models import Parcel, Envelop, Direction, ParcelDimension

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
    
    @staticmethod
    def get_region_from(instance: Parcel) -> Region:
        region_from = instance.direction.get(type=1).district.region
        return region_from
    
    @staticmethod
    def get_district_to(instance: Parcel) -> District:
        district_to = instance.direction.get(type=2).district
        return district_to
    
    def calculate_dimension_price(self):
        parcel_dimension = self.instance.dimension
        if dimension_price_obj := Envelop.objects.filter(
            Q(distance__from_region = self.from_region) & 
            Q(distance__to_district = self.to_district) & 
            Q(dimension__length__lte = parcel_dimension.length) | 
            Q(dimension__width__lte = parcel_dimension.width) | 
            Q(dimension__height__lte = parcel_dimension.height)
        ):
            dimension_price_obj = dimension_price_obj.last()
        else:
            dimension_price_obj = Envelop.objects.filter(
                Q(distance__from_region = self.from_region) & 
                Q(distance__to_district = self.to_district)).first()
        price = float(dimension_price_obj.price)
        dimension_weight = dimension_price_obj.dimension.weight
        if dif := parcel_dimension.weight - dimension_weight > dimension_weight:
            price += float(dimension_price_obj.kilo) * dif
        
        self.instance.payment.envelop = dimension_price_obj
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
            except Envelop.DoesNotExist:
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
        price = dimension_price + packaging_price + delivery_price
        bonus = price * 0.05
        self.instance.sender.points += bonus
        self.instance.save()
        return price
