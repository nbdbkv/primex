from django.core.signals import request_finished
from django.dispatch import receiver
import math
from django.db.models.signals import post_save, pre_save
from .models import Parcel

@receiver(pre_save, sender = Parcel)
def setUserInfo(sender, instance, **kwargs):
    # instance.sender_info.phone  = instance.sender.phone
    # instance.sender_info.info = instance.sender.info
    # instance.sender_info.region = instance.sender.region.name
    # instance.sender_info.city = instance.sender.city.name
    # instance.sender_info.save()
    pass

@receiver(post_save, sender=Parcel)

def calculateParcelPrice(sender,instance, **kwargs):
    price = instance.parcel_info.calculateParcelPrice(instance.location_info.to_location.town, instance.location_info.to_location.area, instance.package_type)
    delivery_time = instance.location_info.to_location.delivery_time()
    code = instance.location_info.to_location.generateCodeForParcel() + str(instance.id)
    instance.price = price
    instance.code = code
    instance.delivery_time = delivery_time

    # BONUS
    instance.sender.points = math.floor((price / 100) * 5)
    instance.sender.save()






