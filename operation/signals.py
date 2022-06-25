from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from operation.models import Parcel
from operation.tasks import (
    tg_parcel_operator,
    tg_parcel_subadmin,
    tg_parcel_to_operator,
)
from operation.choices import DeliveryStatusChoices

from datetime import timedelta


@receiver(post_save, sender=Parcel)
def send_tg_message(sender, instance, created, **kwargs):
    if created:
        tg_parcel_operator.apply_async(
            (instance.code,), eta=now() + timedelta(seconds=30)
        )
        tg_parcel_subadmin.apply_async(
            (instance.code,), eta=now() + timedelta(seconds=600)
        )
    elif instance.status.title == DeliveryStatusChoices.ON_THE_WAY:
        tg_parcel_to_operator.apply_async(
            (instance.code,), eta=now() + timedelta(seconds=30)
        )