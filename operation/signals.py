from django.core.signals import request_finished
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import Parcel

@receiver(pre_save, sender=Parcel)

def calculateParcelPrice(sender,instance, **kwargs):
    price = instance.parsel_info.calculateParcelPrice(instance.location_info.from_location.town,instance.location_info.from_location.area, instance.envelope_type)
    instance.price = price

