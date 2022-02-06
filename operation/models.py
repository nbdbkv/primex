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
    price = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='цена')
    code = models.CharField(max_length=10, verbose_name='код')
    class Meta:
        verbose_name = 'Район'

    def __str__(self):
        return self.name

class Town(models.Model):
    name = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='цена')
    code = models.CharField(max_length=10, verbose_name='код')
    class Meta:
        verbose_name = 'Город'

    def __str__(self):
        return self.name

class Direction(DoubleGisMixin, models.Model):
    town = models.ForeignKey(Town, on_delete=models.CASCADE, verbose_name='город')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name='район', blank=True)
    street = models.CharField(max_length=30, verbose_name='улица', blank=True)
    number = models.CharField(max_length=25, verbose_name='номер кв', blank=True)
    location = fields.GeoLocationField(verbose_name='локация', blank=True)
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
        return f'{self.town} {self.area.name} {self.street} {self.number}'

class Directions(models.Model):
    from_location = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='from+',  verbose_name='Oт куда')
    to_location = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='to', verbose_name='Куда')

    class Meta:
        verbose_name = 'Направление'
    def __str__(self):
        return f'{self.from_location.town} {self.from_location.street} {self.from_location.number} -> {self.to_location.town} {self.to_location.street} {self.to_location.number}'

class ParcelOption(models.Model):
    name = models.CharField(max_length=255)
    class Meta:
        verbose_name = "Варианты посылок"

    def __str__(self):
        return self.name

class Envelope(models.Model):
    name = models.CharField(max_length=40)
    price = models.DecimalField(max_digits=30, decimal_places=2, blank=True)
    class Meta:
        verbose_name = 'Конверт'
    def __str__(self):
        return self.name


class ParcelInfo(models.Model):
    width = models.FloatField(verbose_name='ширина', blank=True)
    lenght = models.FloatField(verbose_name='длина', blank=True)
    hight = models.FloatField(verbose_name='высота', blank=True)
    weight = models.FloatField(verbose_name='масса', blank=True)
    envelope = models.ForeignKey(Envelope, on_delete=models.CASCADE)
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
    company = models.CharField(max_length=35, verbose_name='Называние компании', blank=True)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        verbose_name = 'Данные получателя'

    def __str__(self):
        return self.first_name

class ParcelDate(models.Model):
    create_time = models.DateTimeField(verbose_name='Дата сдачи груза')
    delivery_time = models.DateTimeField(verbose_name='Дата доставки', null=True)
    class Meta:
        verbose_name = 'Дата и время'
    def __str__(self):
        return str(self.create_time)

class Package(models.Model):
    package_name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        verbose_name = 'Упаковка'
    def __str__(self):
        return self.package_name

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
    create_at = models.ForeignKey(ParcelDate, on_delete=models.CASCADE, related_name='created_at')
    price = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name='Сумма', null=False)
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.CASCADE, verbose_name='Тип доставки')
    status = models.ForeignKey(ParcelStatus, models.CASCADE, verbose_name='Статус', default=1)
    pay_satus = models.CharField(max_length=30, choices=PAY_STATUS, verbose_name='статус оплаты')
    location_info = models.ForeignKey(Directions, on_delete=models.CASCADE, verbose_name='направления')
    recipient_info = models.ForeignKey(Recipient, on_delete=models.CASCADE,  verbose_name='Получатель')
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, verbose_name='Cпосоп оплаты', default=1)
    package_type = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='package', verbose_name='Упаковка')
    delivery_date = models.ForeignKey(ParcelDate, on_delete=models.CASCADE, related_name='delivery_date')
    code = models.CharField(max_length=15, verbose_name='Код', default='0')

    class Meta:
        verbose_name = 'Посылка'

    def __str__(self):
        return self.code
