from django.db.models import Q

from account.models import Region, City, District
from operation.models import Parcel, PriceList, PriceEnvelop, Direction, ParcelDimension, DimensionPrice

from uuid import uuid4


def get_parcel_code(direction: dict) -> str:
    city = direction.get('city')
    code = city.region.code + city.code
    if district := direction.get('district'):
        code += district.code
    code += str(uuid4())[:15-len(code)]
    return code


class CalculateParcelPrice:
    
    def __init__(self, instance: Parcel):
        self.instance = instance
        self.from_region = self.get_region_from(instance)
        self.to_district = self.get_district_to(instance)
    
    @staticmethod
    def get_region_from(instance: Parcel) -> Region:
        region_from = instance.direction.get(type=1)
        return region_from
    
    @staticmethod
    def get_district_to(instance: Parcel) -> City:
        district_to = instance.direction.get(type=2)
        return district_to
    
    def calculate_dimension_price(self):
        parcel_dimension = self.instance.dimension
        if dimension_price_obj := DimensionPrice.objects.filter(
            Q(from_region = self.from_region) & 
            Q(to_district = self.to_district) & 
            Q(dimension__length__lte = parcel_dimension.length) | 
            Q(dimension__width__lte = parcel_dimension.width) | 
            Q(dimension__height__lte = parcel_dimension.height)
        ):
            dimension_price_obj = dimension_price_obj.last()
        else:
            dimension_price_obj = DimensionPrice.objects.get(
                Q(from_region = self.from_region) & 
                Q(to_district = self.to_district))
        price = float(dimension_price_obj.price)
        if dif := parcel_dimension.weight // dimension_price_obj.dimension.weight > 1:
            price += float(dimension_price_obj.price_list.kilo) * dif
        
        self.instance.payment.price_list = dimension_price_obj.price_list
        self.instance.save()
        
        return price
        
    def calculate_envelop_price(self):
        envelop = PriceEnvelop.objects.get(
            Q(from_region = self.from_region) & 
            Q(to_district = self.to_district) &
            Q(envelop = self.instance.payment.envelop)
        )
        price = float(envelop.price)
        self.instance.payment.envelop = envelop
        self.instance.save()
        return price
    
    def calculate_packaging_price(self):
        packaging = self.instance.payment.packaging.all()
        price = 0
        for pack in packaging:
            price += float(pack.price * pack.quantity)
        return price

    def calculate_delivery_price(self):
        delivery = self.instance.payment.delivery_type
        price = float(delivery.price)
        return price

    @property
    def price(self):
        dimension_price = self.calculate_dimension_price()
        envelop_price = self.calculate_envelop_price()
        packaging_price = self.calculate_packaging_price()
        delivery_price = self.calculate_delivery_price()
        price = dimension_price + envelop_price + packaging_price + delivery_price
        return price
