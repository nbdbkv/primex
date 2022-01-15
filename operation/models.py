from django.db import models

from django.db import models
from account.models import User
from datetime import datetime

class DeliveryType(models.Model):
    TYPE_CHOICES = [
        ("авия", "авия"),
        ("авто", "авто")
    ]
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Тип доставки'

    def __str__(self):
        return self.name


class ParcelStatus(models.Model):
    PARCEL_STATUS = [
        ("доставлено", "доставлено"),
        ("обработке", "обработке"),
        ("В пути", "В пути")
    ]
    name = models.CharField(max_length=20, choices=PARCEL_STATUS)

    class Meta:
        verbose_name = 'Статус'

    def __str__(self):
        return self.name

class Direction(models.Model):
    from_location = models.CharField(max_length=255, verbose_name='от куда')
    to_location = models.CharField(max_length=255, verbose_name='куда')
    dictance_between = models.CharField(max_length=255, verbose_name='дистанция')

    class Meta:
        verbose_name = 'Направление'
    def __str__(self):
        return self.to_location


class ParcelInfo(models.Model):
    weight = models.FloatField(verbose_name='масса')
    hight = models.FloatField(verbose_name='высота')
    lenght = models.FloatField(verbose_name='длина')
    width = models.FloatField(verbose_name='ширина')
    volume = models.FloatField(verbose_name='объем')

    class Meta:
        verbose_name = 'Информация о посылке'

class UserInfo(models.Model):
    phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=20)
    zip_code = models.IntegerField()

    def __str__(self):
        return self.first_name

class ParcelOption(models.Model):
    TYPE_CHOICES = [
        ('хрупкий', 'хрупкий'),
        # etc
    ]
    name = models.CharField(max_length=255, choices=TYPE_CHOICES)

    class Meta:
        verbose_name = "Варианты посылок"

    def __str__(self):
        return self.name


class DestinationType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name  = 'Тип назначения'

    def __str__(self):
        return self.name

class PaymentType(models.Model):
    TYPE_CHOICES = [
        ("mbank", "Мбанк"),
        ("cash", "Наличка")
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="cash")

    class Meta:
        verbose_name = 'Тип оплата'

    def __str__(self):
        return self.type



class Parcel(models.Model):
    PAY_STATUS = [
        ('paid', 'Оплачено'),
        ('not paid', 'Не оплачено')
    ]
    title = models.CharField(max_length=255, verbose_name='Называние')
    description = models.CharField(max_length=255, verbose_name='Описание')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель')
    sender_info = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name='данных отправителя')
    parsel_info = models.ForeignKey(ParcelInfo, on_delete=models.CASCADE, verbose_name='информация о посылке')
    create_at = models.DateField(default=datetime.now)
    price = models.DecimalField(max_digits=30, decimal_places=2)
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.CASCADE, verbose_name='тип доставки')
    options = models.ForeignKey(ParcelOption, models.CASCADE, verbose_name='варианты посылок')
    status = models.ForeignKey(ParcelStatus, models.CASCADE, verbose_name='Статус')
    pay_satus = models.CharField(max_length=25, choices=PAY_STATUS, verbose_name='статус оплаты')
    location_info = models.ForeignKey(Direction, on_delete=models.CASCADE, verbose_name='направления')
    recipient_info = models.CharField(max_length=255,  verbose_name='Получатель')
    destination_type = models.ForeignKey(DestinationType, on_delete=models.CASCADE, verbose_name='тип назначения')
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, verbose_name='способ оплаты')

    class Meta:
        verbose_name = 'Посылка'

    def __str__(self):
        return self.title
