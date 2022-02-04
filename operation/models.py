from django.db import models
from account.models import User
from .calculator import calculatePrice, deliveryTime, generateCode
from django_2gis_maps import fields
from django_2gis_maps.mixins import DoubleGisMixin

class DeliveryType(models.Model):
    name = models.CharField(max_length=50)
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
        verbose_name = 'Район'

    def __str__(self):
        return self.name

class Town(models.Model):
    name = models.CharField(max_length=20)
    class Meta:
        verbose_name = 'Город'

    def __str__(self):
        return self.name
class Direction(DoubleGisMixin, models.Model):
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    street = models.CharField(max_length=20, verbose_name='улица')
    number = models.CharField(max_length=10,  verbose_name='номер кв', default='')
    location = fields.GeoLocationField(verbose_name='локация', default=0)

    class Meta:
        verbose_name = 'Направления'

    def delivery_time(self):
        town = self.town.__str__()
        area = self.area.__str__()

        return deliveryTime(town, area)

    def generateCodeForParcel(self):
        town = self.town.__str__()
        area = self.area.__str__()
        return generateCode(town, area)

    def __str__(self):
        return f'{self.town} {self.area} {self.street} {self.number}'

class Directions(models.Model):
    from_location = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='from+',  verbose_name='Oт куда')
    to_location = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='to', verbose_name='Куда')

    class Meta:
        verbose_name = 'Направление'
    def __str__(self):
        return f'{self.from_location.town} {self.from_location.area} {self.from_location.street} {self.from_location.number} -> {self.to_location.town} {self.to_location.area} {self.to_location.street} {self.to_location.number}'

class ParcelOption(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Варианты посылок"

    def __str__(self):
        return self.name

class ParcelInfo(models.Model):
    CHOICES = ((1, 'Nasdaq'), (2, 'Nyse'), (3, 'Amex'),)
    width = models.FloatField(verbose_name='ширина', null=True)
    lenght = models.FloatField(verbose_name='длина', null=True)
    hight = models.FloatField(verbose_name='высота', null=True)
    weight = models.FloatField(verbose_name='масса', null=True)
    presumably = models.FloatField(verbose_name='примерно', null=True)
    options = models.ManyToManyField(ParcelOption, related_name='options', verbose_name='варианты посылок')


    class Meta:
        verbose_name = 'Параметры груза'

    def calculateParcelPrice(self, townLocation, areaLocation, envelop):
        return calculatePrice(self.weight, self.hight, self.lenght, self.width, townLocation, areaLocation, envelop)

    def __str__(self):
        return f'{self.width} {self.lenght} {self.hight} {self.weight}'

class UserInfo(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    company = models.CharField(max_length=50, null=True)

    class Meta:
        verbose_name = 'Данные отправителя'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class PaymentType(models.Model):
    type = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Тип оплата'

    def __str__(self):
        return self.type

class Recipient(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    phone = models.CharField(max_length=15, verbose_name='Номер телефона')
    company = models.CharField(max_length=35, verbose_name='Называние компании', default='0')
    email = models.EmailField(null=True)

    class Meta:
        verbose_name = 'Данные получателя'

    def __str__(self):
        return self.first_name

class DeliveryDate(models.Model):
    date = models.DateTimeField(verbose_name='Дата сдачи груза')
    class Meta:
        verbose_name = 'Дата сдачи груза'
    def __str__(self):
        return str(self.date)

class Envelope(models.Model):
    name = models.CharField(max_length=40)
    class Meta:
        verbose_name = 'Упаковка'
    def __str__(self):
        return self.name

class Parcel(models.Model):
    PAY_STATUS = [
        ('1', 'Оплачено'),
        ('0', 'Не оплачено')
    ]
    ENVELOPE = [
        ('NULL', 'Не выбрать'),
        ('c5', 'Конверт С5'),
        ('c4', 'Конверт С4'),
        ('c3', 'Конверт С3')
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель')
    sender_info = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name='Мои данные')
    recipient_info = models.ForeignKey(Recipient, on_delete=models.CASCADE, verbose_name='Данные получателя')
    parcel_info = models.ForeignKey(ParcelInfo, on_delete=models.CASCADE, verbose_name='Параметры груза')
    create_at = models.DateTimeField(verbose_name='Дата сдачи груза')
    price = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name='Сумма', null=False)
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.CASCADE, verbose_name='Тип доставки')
    status = models.ForeignKey(ParcelStatus, models.CASCADE, verbose_name='Статус')
    pay_satus = models.CharField(max_length=30, choices=PAY_STATUS, verbose_name='статус оплаты')
    location_info = models.ForeignKey(Directions, on_delete=models.CASCADE, verbose_name='направления')
    recipient_info = models.ForeignKey(Recipient, on_delete=models.CASCADE,  verbose_name='Получатель')
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, verbose_name='Cпосоп оплаты', default=1)
    envelope_type = models.ForeignKey(Envelope, on_delete=models.CASCADE, related_name='package', verbose_name='Упаковка')
    delivery_date = models.ForeignKey(DeliveryDate, on_delete=models.CASCADE, verbose_name='Дата доставки')
    code = models.CharField(max_length=15, verbose_name='Код', default='0')

    class Meta:
        verbose_name = 'Посылка'

    def __str__(self):
        return self.code
