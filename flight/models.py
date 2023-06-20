import barcode

from barcode.writer import ImageWriter
from io import BytesIO

from django.db import models
from django.core.files import File
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel

from flight.choices import StatusChoices, get_status


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(db_index=True, auto_now=True, verbose_name=_('Дата изменения'))
    arrived_at = models.DateTimeField(db_index=True, null=True, blank=True, verbose_name=_('Дата прибытия'))

    class Meta:
        abstract = True

    def get_statuses(self):
        return {key: value for (key, value) in StatusChoices.choices[2:]}


class TrackCode(SingletonModel):
    code = models.IntegerField(default=0)


class Destination(models.Model):
    point = models.CharField(max_length=100, verbose_name=_('Пункт назначения'))
    price_per_kg = models.CharField(max_length=8, verbose_name=_('Цена за кг в $'))
    currency = models.CharField(max_length=8, verbose_name=_('Курс валют'))

    class Meta:
        verbose_name = _("пункт назначения")
        verbose_name_plural = _("Направления")

    def __str__(self):
        return f'{self.point} / {self.price_per_kg}$'


class Flight(TimeStampedModel):
    # Рейс
    numeration = models.CharField(db_index=True, max_length=64, verbose_name=_('Нумерация рейсов'))
    code = models.CharField(db_index=True, max_length=64, verbose_name=_('Код рейса'))
    status = models.PositiveIntegerField(default=StatusChoices.FORMING, choices=StatusChoices.choices,
                                         verbose_name=_('Статус'), null=True, blank=True,)
    is_archive = models.BooleanField(default=False, verbose_name=_('Архив'))

    class Meta:
        verbose_name = _('рейс')
        verbose_name_plural = _('Рейсы')

    def __str__(self):
        if self.code:
            return self.code
        else:
            return ''


class Arrival(Flight):
    # Поступления

    class Meta:
        proxy = True
        verbose_name = _('прибывший рейс')
        verbose_name_plural = _('Поступления')


class Delivery(Flight):
    # Поступления

    class Meta:
        proxy = True
        verbose_name = _('готовый к выдаче рейс')
        verbose_name_plural = _('Выдача посылок')


class Archive(Flight):
    # Архив Рейсов

    class Meta:
        proxy = True
        verbose_name = _('выданный рейс')
        verbose_name_plural = _('Архив рейсов')


class Box(TimeStampedModel):
    # Коробка
    destination = models.ForeignKey(
        Destination, on_delete=models.CASCADE, related_name='boxes', verbose_name=_('Направление'), null=True,
        blank=True,
    )
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='box', verbose_name=_('Рейс коробки'),
                               null=True, blank=True)
    number = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Номер'), )
    code = models.CharField(max_length=64, verbose_name=_('Код коробки'), null=True, blank=True)
    track_code = models.CharField(max_length=64, verbose_name=_('Трек-Код'), null=True, blank=True)
    weight = models.DecimalField(
        max_digits=10, decimal_places=3, verbose_name=_('Вес с коробкой'), null=True, blank=True,
    )
    comment = models.TextField(max_length=128, verbose_name=_('Комментарий'), null=True, blank=True)
    status = models.PositiveIntegerField(choices=get_status()[2:7], verbose_name=_('Статус'), null=True, blank=True,)

    class Meta:
        verbose_name = _('коробку')
        verbose_name_plural = _('Коробки')

    def __str__(self):
        if self.code:
            return self.code
        else:
            return ''


class BaseParcel(TimeStampedModel):
    # Посылка
    box = models.ForeignKey(
        Box, on_delete=models.CASCADE, related_name='base_parcel', null=True, blank=True,
        verbose_name=_('Коробка посылки'),
    )
    track_code = models.CharField(db_index=True, max_length=64, verbose_name=_('Трек-Код'))
    barcode = models.ImageField(
        upload_to='flight/baseparcel/barcode', null=True, blank=True, verbose_name=_("Штрих-Код"),
    )
    client_code = models.CharField(db_index=True, max_length=64, null=True, blank=True, verbose_name=_('Код клиента'))
    phone = models.CharField(db_index=True, max_length=16, null=True, blank=True, verbose_name=_('Телефон клиента'))
    shelf = models.CharField(max_length=16, null=True, blank=True, verbose_name=_('Полка'))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Цена'))
    weight = models.DecimalField(max_digits=8, decimal_places=3, verbose_name=_('Вес'))
    cost_usd = models.DecimalField(
        max_digits=8, decimal_places=2,  null=True, blank=True, verbose_name=_('Стоимость в $'),
    )
    cost_kgs = models.IntegerField(null=True, blank=True, verbose_name=_('Стоимость в сомах'))
    note = models.CharField(max_length=128, null=True, blank=True, verbose_name=_('Примечание'))
    delivered_at = models.DateTimeField(db_index=True, null=True, blank=True, verbose_name=_('Дата выдачи'))
    status = models.PositiveIntegerField(default=StatusChoices.FORMING, null=True, blank=True, choices=get_status())

    class Meta:
        verbose_name = _('base_parcel')
        verbose_name_plural = _('base_parcels')

    def __str__(self):
        if self.track_code:
            return self.track_code
        else:
            return ''

    def save(self, *args, **kwargs):
        COD128 = barcode.get_barcode_class('code128')
        rv = BytesIO()
        code = COD128(f'{self.track_code}', writer=ImageWriter()).write(rv)
        self.barcode.save(f'{self.track_code}.png', File(rv), save=False)
        currency = self.box.destination.currency
        self.cost_kgs = int(float(self.cost_usd) * float(currency))
        super(BaseParcel, self).save(*args, **kwargs)


class Unknown(BaseParcel):
    # Неизвестные заказы

    class Meta:
        proxy = True
        verbose_name = _('неизвестную посылку')
        verbose_name_plural = _('Неизвестные посылки')


class DeliveryBaseParcel(BaseParcel):

    class Meta:
        proxy = True
        verbose_name = _('готовую к выдаче посылку')
        verbose_name_plural = _('Распечатка посылок')


class Media(models.Model):
    # Медиа
    title = models.CharField(_("Название"), max_length=127,)
    icon = models.ImageField(_("Иконка"), upload_to='flight/media/icon')
    image = models.ImageField(_("Изображение"), upload_to='flight/media/image', null=True, blank=True,)
    video = models.FileField(_("Видео"), upload_to='flight/media/video', null=True, blank=True,)

    class Meta:
        verbose_name = _("медиа")
        verbose_name_plural = _("Медиа")

    def __str__(self):
        return self.title


class Rate(models.Model):
    weight = models.CharField(_('Вес'), max_length=100,)
    service_type = models.CharField(_('Вид услуги'), max_length=100,)
    air = models.CharField(_('Китай (Авиа)'), max_length=100, null=True, blank=True,)
    truck = models.CharField(_('Китай (Авто)'), max_length=100, null=True, blank=True,)
    commission = models.CharField(_('Комиссия'), max_length=100, null=True, blank=True,)

    class Meta:
        verbose_name = _("тариф")
        verbose_name_plural = _("Тарифы")

    def __str__(self):
        return self.weight


class Contact(models.Model):
    social = models.CharField(_('Социальная сеть'), max_length=100,)
    icon = models.ImageField(_('Иконка'), upload_to='flight/contact', null=True, blank=True,)

    class Meta:
        verbose_name = _("контакт")
        verbose_name_plural = _("Контакты")

    def __str__(self):
        return self.social
