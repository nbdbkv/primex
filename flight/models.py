from django.db import models
from django.utils.translation import gettext_lazy as _

LOW = 0
NORMAL = 1
HIGH = 2
STATUS_CHOICES = (
    (LOW, _('Формируется')),
    (NORMAL, _('В пути')),
    (HIGH, _('Прибыл')),
)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(db_index=True, auto_now=True, verbose_name=_('Дата изменения'))

    class Meta:
        abstract = True


class Flight(TimeStampedModel):
    # Рейс
    numeration = models.CharField(db_index=True, max_length=64, verbose_name=_('Нумерация рейсов'))
    code = models.CharField(db_index=True, max_length=64, verbose_name=_('Код'))
    quantity = models.PositiveIntegerField(verbose_name=_('Количество мест (коробка)'))
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_('weight flight'), null=True, blank=True)
    cube = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('cube'), null=True, blank=True)
    density = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('density'), null=True, blank=True)
    consumption = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('consumption flight'), null=True,
                                      blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('price'), null=True, blank=True)
    sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('sum'), null=True, blank=True)
    status = models.PositiveIntegerField(default=LOW, choices=STATUS_CHOICES, verbose_name=_('status'),
                                         null=True, blank=True)

    class Meta:
        verbose_name = _('flight')
        verbose_name_plural = _('flights')


class Box(TimeStampedModel):
    # Коробка
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='box', verbose_name=_('flightfk'),
                               null=True, blank=True)
    code = models.CharField(db_index=True, max_length=64, verbose_name=_('Код'))
    track_code = models.CharField(db_index=True, max_length=64, verbose_name=_('Трек-Код'))
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_('weight box'), null=True, blank=True)
    consumption = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('consumption box'), null=True,
                                      blank=True)

    class Meta:
        verbose_name = _('box')
        verbose_name_plural = _('boxes')


class BaseParcel(TimeStampedModel):
    # Посылка
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='base_parcel', verbose_name=_('boxfk'),
                            null=True, blank=True)
    code = models.CharField(db_index=True, max_length=64, verbose_name=_('Код'))
    track_code = models.CharField(db_index=True, max_length=64, verbose_name=_('Трек-Код'))
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_('weight box'))

    # Габариты
    width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('width base'))
    length = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('length base'))
    height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('height base'))

    comment = models.TextField(verbose_name=_('comment'), null=True, blank=True)

    class Meta:
        verbose_name = _('base_parcel')
        verbose_name_plural = _('base_parcels')
