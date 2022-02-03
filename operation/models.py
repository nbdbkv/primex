import django
from django.db import models
from account.models import User
from datetime import datetime
from .calculator import calculatePrice, deliveryTime, generateCode
from  django.utils import timezone

class DeliveryType(models.Model):
    TYPE_CHOICES = [
        ("авия", "авия"),
        ("авто", "авто")
    ]
    name = models.CharField(max_length=50, choices=TYPE_CHOICES)

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

class Area(models.Model):
    name = models.CharField(max_length=20)
    class Meta:
        verbose_name = 'Area'

    def __str__(self):
        return self.name

class Town(models.Model):
    name = models.CharField(max_length=20)
    class Meta:
        verbose_name = 'Town'

    def __str__(self):
        return self.name
class Direction(models.Model):
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    street = models.CharField(max_length=20, verbose_name='улица')
    number = models.CharField(max_length=10,  verbose_name='номер кв', default=None)

    class Meta:
        verbose_name = 'Direction'

    def __str__(self):
        return f'{self.town} {self.area} {self.street} {self.number}'

    def delivery_time(self):
        return deliveryTime(self.town.__str__(), self.area.__str__())

    def generateCodeForParcel(self):
        return generateCode(self.town.__str__(), self.area.__str__())

class Directions(models.Model):
    name = models.CharField(max_length=20)
    from_location = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='from+',  verbose_name='Oт куда')
    to_location = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='to', verbose_name='Куда')
    dictance_between = models.CharField(max_length=255, verbose_name='дистанция')

    class Meta:
        verbose_name = 'Направление'

    def __str__(self):
        return self.name


class ParcelInfo(models.Model):
    weight = models.FloatField(verbose_name='масса')
    hight = models.FloatField(verbose_name='высота')
    lenght = models.FloatField(verbose_name='длина')
    width = models.FloatField(verbose_name='ширина')
    volume = models.FloatField(verbose_name='объем')

    class Meta:
        verbose_name = 'Информация о посылке'

    def calculateParcelPrice(self, townLocation, areaLocation, envelop):
        return calculatePrice(self.weight, self.hight, self.lenght, self.width, self.volume, townLocation, areaLocation, envelop)


class UserInfo(models.Model):
    phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=20)
    region = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    zip_code = models.IntegerField(default=None)


class ParcelOption(models.Model):
    name = models.CharField(max_length=255)

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
    type = models.CharField(max_length=30, default="cash")

    class Meta:
        verbose_name = 'Тип оплата'

    def __str__(self):
        return self.type

class Envelope(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Envelope'

    def __str__(self):
        return self.name

class Parcel(models.Model):
    PAY_STATUS = [
        ('paid', 'Оплачено'),
        ('not paid', 'Не оплачено')
    ]
    ENVELOPE = [
        ('NULL', 'Не выбрать'),
        ('c5', 'Конверт С5'),
        ('c4', 'Конверт С4'),
        ('c3', 'Конверт С3')
    ]
    title = models.CharField(max_length=255, verbose_name='Называние')
    description = models.CharField(max_length=255, verbose_name='Описание')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель')
    sender_info = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name='данных отправителя')
    parsel_info = models.ForeignKey(ParcelInfo, on_delete=models.CASCADE, verbose_name='информация о посылке')
    create_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.CASCADE, verbose_name='тип доставки')
    options = models.ManyToManyField(ParcelOption, related_name='options', verbose_name='варианты посылок')
    status = models.ForeignKey(ParcelStatus, models.CASCADE, verbose_name='Статус')
    pay_satus = models.CharField(max_length=30, choices=PAY_STATUS, verbose_name='статус оплаты')
    location_info = models.ForeignKey(Directions, on_delete=models.CASCADE, verbose_name='направления')
    recipient_info = models.CharField(max_length=255,  verbose_name='Получатель')
    #destination_type = models.ForeignKey(DestinationType, on_delete=models.CASCADE, verbose_name='тип назначения')
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, verbose_name='способ оплаты')
    envelope_type = models.CharField(max_length=30, choices=ENVELOPE, verbose_name='envelope type')
    delivery_time = models.CharField(max_length=10, verbose_name='Срок доставки', null=True)
    code = models.CharField(max_length=15, verbose_name='Код', null=True)

    class Meta:
        verbose_name = 'Посылка'

    def __str__(self):
        return self.title