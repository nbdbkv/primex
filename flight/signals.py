# from django.db.models import Q
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from fcm_django.models import FCMDevice
# from firebase_admin.messaging import Message, Notification
#
# from account.models import User
# from flight.models import BaseParcel
#
#
# @receiver(post_save, sender=BaseParcel)
# def send_fcm_when_forming(sender, instance, created, **kwargs):
#     if created:
#         user = User.objects.exclude(code_logistic=None).filter(
#             Q(code_logistic=instance.client_code) | (Q(phone=instance.phone))
#         ).values('pk')
#         if user:
#             devices = FCMDevice.objects.filter(user_id__in=user)
#             for device in devices:
#                 device.send_message(
#                     Message(
#                         notification=Notification(
#                             title='Taura Express',
#                             body=f'Посылка {instance.track_code} формируется на складе в Китае.'
#                         )
#                     )
#                 )
#
#
# @receiver(post_save, sender=BaseParcel)
# def send_fcm_on_arrival(sender, instance, created, **kwargs):
#     if not created and instance.status == 2:
#         user = User.objects.exclude(code_logistic=None).filter(
#             Q(code_logistic=instance.client_code) | (Q(phone=instance.phone))
#         ).values('pk')
#         if user:
#             devices = FCMDevice.objects.filter(user_id__in=user)
#             for device in devices:
#                 device.send_message(
#                     Message(
#                         notification=Notification(
#                             title='Taura Express',
#                             body=f'Посылка {instance.track_code} прибыла на склад в КР.'
#                         )
#                     )
#                 )
#
#
# @receiver(post_save, sender=BaseParcel)
# def send_fcm_when_ready(sender, instance, created, **kwargs):
#     if not created and instance.status == 4:
#         user = User.objects.exclude(code_logistic=None).filter(
#             Q(code_logistic=instance.client_code) | (Q(phone=instance.phone))
#         ).values('pk')
#         if user:
#             devices = FCMDevice.objects.filter(user_id__in=user)
#             for device in devices:
#                 device.send_message(
#                     Message(
#                         notification=Notification(
#                             title='Taura Express',
#                             body=f'Посылка {instance.track_code} готова к выдаче. Заберите посылку.'
#                         )
#                     )
#                 )
