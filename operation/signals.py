from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from operation.models import Parcel
from operation.tasks import new_parcel

from datetime import timedelta


@receiver(post_save, sender=Parcel)
def send_tg_message(sender, instance, created, **kwargs):
    if created:
        new_parcel.apply_async((instance.code, ), eta=now() + timedelta(seconds=300))
