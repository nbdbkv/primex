from django.db import models
from account.models import User
from datetime import datetime

class DeliveryType(models.Model):
    pass

class ParcelOption(models.Model):
    pass

class ParcelStatus(models.Model):
    pass

class Direction(models.Model):
    pass

class ParcelInfo(models.Model):
    pass


class UserInfo(models.Model):
    pass

class ParcelOption(models.Model):
    pass

class DestinationType(models.Model):
    pass

class PaymentType(models.Model):
    pass

class Parcel(models.Model):
    title = models.CharField(max_length=255, verbose_name='Называние')
    description = models.CharField(max_length=255, verbose_name='Описание')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель')
    sender_info = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name='данных отправителя')
    parsel_info = models.ForeignKey(ParcelInfo, on_delete=models.CASCADE, verbose_name='информация о посылке')
    create_at = models.DateField(default=datetime.now)
    price = models.DecimalField()
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.CASCADE, verbose_name='тип доставки')
    options = models.ForeignKey(ParcelOption, models.CASCADE, verbose_name='варианты посылок')
    status = models.ForeignKey(ParcelStatus, models.CASCADE, verbose_name='Статус')



