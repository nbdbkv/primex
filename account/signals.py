from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import User
from account.choices import UserRole
from account.roles import courier, operator, subadmin


@receiver(post_save, sender=User)
def add_permissions_signal(sender, instance, created, **kwargs):
    if created:
        if instance.role == UserRole.OPERATOR:
            print("hellllllllooooooo")
            perm = operator.get_permission()
            for permission in perm:
                instance.user_permissions.add(permission)
        elif instance.role == UserRole.SUBADMIN:
            perm = subadmin.get_permission()
            for permission in perm:
                instance.user_permissions.add(permission)
