from django.db import models
from account.models import User
from .calculator import calculatePrice, deliveryTime, generateCode

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
class Direction(models.Model):
    town = models.ForeignKey(Town, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    street = models.CharField(max_length=20, verbose_name='улица')
    number = models.CharField(max_length=10,  verbose_name='номер кв', default=None)

    class Meta:
        verbose_name = 'Направления'

    def __str__(self):
        return f'{self.town} {self.area} {self.street} {self.number}'

    def delivery_time(self):
        return deliveryTime(self.town.__str__(), self.area.__str__())

    def generateCodeForParcel(self):
        return generateCode(self.town.__str__(), self.area.__str__())

class Directions(models.Model):
    from_location = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='from+',  verbose_name='Oт куда')
    to_location = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='to', verbose_name='Куда')
    dictance_between = models.CharField(max_length=255, verbose_name='дистанция', default='0')

    class Meta:
        verbose_name = 'Направление'

    def __str__(self):
        return f'{self.from_location.town} {self.from_location.area} {self.from_location.street} {self.from_location.number} -> {self.to_location.town} {self.to_location.area} {self.to_location.street} {self.to_location.number}'


class ParcelInfo(models.Model):
    width = models.FloatField(verbose_name='ширина', null=True)
    lenght = models.FloatField(verbose_name='длина', null=True)
    hight = models.FloatField(verbose_name='высота', null=True)
    weight = models.FloatField(verbose_name='масса', null=True)
    presumably = models.FloatField(verbose_name='примерно', null=True)

    class Meta:
        verbose_name = 'Параметры груза'

    def calculateParcelPrice(self, townLocation, areaLocation, envelop):
        return calculatePrice(self.weight, self.hight, self.lenght, self.width, townLocation, areaLocation, envelop)

    def __str__(self):
        return f'{self.width} {self.lenght} {self.hight} {self.weight}'

class UserInfo(models.Model):

    info = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    region = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=20, null=True)
    zip_code = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'Данные отправителя'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class ParcelOption(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Варианты посылок"

    def __str__(self):
        return self.name


class PaymentType(models.Model):
    type = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Тип оплата'

    def __str__(self):
        return self.type

class Envelope(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Упаковка'

    def __str__(self):
        return self.name

class Recipient(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    phone = models.CharField(max_length=15, verbose_name='Номер телефона')
    company = models.CharField(max_length=35, verbose_name='Называние компании', null=True)
    email = models.EmailField(null=True)

    class Meta:
        verbose_name = 'Данные получателя'

    def __str__(self):
        return self.first_name

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
    title = models.CharField(max_length=255, verbose_name='Называние')
    description = models.CharField(max_length=255, verbose_name='Описание')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель')
    sender_info = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name='Мои данные')
    recipient_info = models.ForeignKey(Recipient, on_delete=models.CASCADE, verbose_name='Данные получателя')
    parsel_info = models.ForeignKey(ParcelInfo, on_delete=models.CASCADE, verbose_name='Параметры груза')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='Время заказа')
    price = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name='Сумма', null=False)
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.CASCADE, verbose_name='Тип доставки')
    options = models.ManyToManyField(ParcelOption, related_name='options', verbose_name='варианты посылок')
    status = models.ForeignKey(ParcelStatus, models.CASCADE, verbose_name='Статус')
    pay_satus = models.CharField(max_length=30, choices=PAY_STATUS, verbose_name='статус оплаты')
    location_info = models.ForeignKey(Directions, on_delete=models.CASCADE, verbose_name='направления')
    recipient_info = models.ForeignKey(Recipient, on_delete=models.CASCADE,  verbose_name='Получатель')
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, verbose_name='Cпосоп оплаты')
    envelope_type = models.CharField(max_length=30, choices=ENVELOPE, verbose_name='Упаковка')
    delivery_time = models.CharField(max_length=10, verbose_name='Дата сдачи груза', null=True)
    code = models.CharField(max_length=15, verbose_name='Код', default='0')

    class Meta:
        verbose_name = 'Посылка'

    def __str__(self):
        return self.title