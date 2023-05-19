from django.db import models
from django.utils.translation import gettext_lazy as _

from flight.choices import StatusChoices, get_status


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(db_index=True, auto_now=True, verbose_name=_('Дата изменения'))
    arrived_at = models.DateTimeField(db_index=True, null=True, blank=True, verbose_name=_('Дата прибытия'))

    class Meta:
        abstract = True

    def get_statuses(self):
        return {key: value for (key, value) in StatusChoices.choices[2:]}


class Flight(TimeStampedModel):
    # Рейс
    numeration = models.CharField(db_index=True, max_length=64, verbose_name=_('Нумерация рейсов'))
    code = models.CharField(db_index=True, max_length=64, verbose_name=_('Код рейса'))
    quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Количество коробки'),)
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_('Вес'), null=True, blank=True)
    cube = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('Куб'), null=True, blank=True)
    density = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('Плотность'), null=True, blank=True)
    consumption = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Расход в $'), null=True,
                                      blank=True)
    status = models.PositiveIntegerField(default=StatusChoices.FORMING, choices=StatusChoices.choices,
                                         verbose_name=_('Статус'), null=True, blank=True,)
    is_archive = models.BooleanField(default=False, verbose_name=_('Архив'))

    class Meta:
        verbose_name = _('Рейс')
        verbose_name_plural = _('Рейсы')

    def __str__(self):
        if self.numeration:
            return self.numeration
        else:
            return ''


class Arrival(Flight):
    # Поступления

    class Meta:
        proxy = True
        verbose_name = _('Поступление')
        verbose_name_plural = _('Поступления')


class Archive(Flight):
    # Архив Рейсов

    class Meta:
        proxy = True
        verbose_name = _('Архив рейс')
        verbose_name_plural = _('Архив рейсов')


class Box(TimeStampedModel):
    # Коробка
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='box', verbose_name=_('Рейс коробки'),
                               null=True, blank=True)
    number = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Номер'), )
    code = models.CharField(max_length=64, verbose_name=_('Код коробки'), null=True, blank=True)
    track_code = models.CharField(max_length=64, verbose_name=_('Трек-Код'), null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_('Вес с коробкой'), null=True, blank=True)
    price = models.CharField(max_length=64, verbose_name=_('Цена за кг в $'), null=True, blank=True)
    consumption = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Расход в $'), null=True, blank=True)
    sum = models.CharField(max_length=64, verbose_name=_('Сумма в $'), null=True, blank=True)
    comment = models.TextField(max_length=128, verbose_name=_('comment'), null=True, blank=True)
    status = models.PositiveIntegerField(choices=get_status()[2:7], verbose_name=_('Статус'), null=True, blank=True,)

    class Meta:
        verbose_name = _('box')
        verbose_name_plural = _('boxes')

    def __str__(self):
        if self.code:
            return self.code
        else:
            return ''


class BaseParcel(TimeStampedModel):
    # Посылка
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='base_parcel',
                            verbose_name=_('Коробка посылки'),
                            null=True, blank=True)
    code = models.CharField(db_index=True, max_length=64, verbose_name=_('Трек-Код'))
    client_code = models.CharField(db_index=True, max_length=64, verbose_name=_('Код клиента'))
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_('Вес'))
    consumption = models.DecimalField(
        max_digits=10, decimal_places=2,  verbose_name=_('Доп. расход в $'), null=True, blank=True,
    )
    status = models.PositiveIntegerField(
        default=StatusChoices.FORMING, choices=get_status(), verbose_name=_('Статус'), null=True, blank=True,
    )

    class Meta:
        verbose_name = _('base_parcel')
        verbose_name_plural = _('base_parcels')

    def __str__(self):
        if self.code:
            return self.code
        else:
            return ''


class Unknown(BaseParcel):
    # Неизвестные заказы

    class Meta:
        proxy = True
        verbose_name = _('Неизвестный заказ')
        verbose_name_plural = _('Неизвестные заказы')


class Media(models.Model):
    # Медиа
    title = models.CharField(_("Название"), max_length=127,)
    image = models.ImageField(_("Изображение"), upload_to='operation/media/image', null=True, blank=True,)
    video = models.FileField(_("Видео"), upload_to='operation/media/video', null=True, blank=True,)

    class Meta:
        verbose_name = _("Медиа")
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
        verbose_name = _("Тариф")
        verbose_name_plural = _("Тарифы")

    def __str__(self):
        return self.weight


class Contact(models.Model):
    social = models.CharField(_('Социальная сеть'), max_length=100,)
    icon = models.ImageField(_('Иконка'), upload_to='operation/contact', null=True, blank=True,)

    class Meta:
        verbose_name = _("Контакт")
        verbose_name_plural = _("Контакты")

    def __str__(self):
        return self.social
