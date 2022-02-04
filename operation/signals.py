from django.core.signals import request_finished
from django.dispatch import receiver
import math
from django.db.models.signals import post_save, pre_save
from .models import Parcel

@receiver(pre_save, sender = Parcel)
def setUserInfo(sender, instance, **kwargs):
    instance.sender_info.phone  = instance.sender.phone
    instance.sender_info.first_name = instance.sender.first_name
    instance.sender_info.last_name = instance.sender.last_name
    instance.sender_info.save()

@receiver(post_save, sender=Parcel)
def calculateParcelPrice(sender,instance, **kwargs):
    price = instance.parcel_info.calculateParcelPrice(instance.location_info.to_location.town, instance.location_info.to_location.area, instance.envelope_type)
    delivery_time = instance.location_info.to_location.delivery_time()
    code = instance.location_info.to_location.generateCodeForParcel() + instance.id.__str__()
    instance.price = price
    instance.code = code
    instance.delivery_time = delivery_time

    # BONUS
    instance.sender.points = math.floor((price / 100) * 5)
    instance.sender.save()






