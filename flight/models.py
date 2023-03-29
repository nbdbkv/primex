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
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_('Вес'), null=True, blank=True)
    cube = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('Куб'), null=True, blank=True)
    density = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('Плотность'), null=True, blank=True)
    consumption = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Расход'), null=True,
                                      blank=True)
    status = models.PositiveIntegerField(default=LOW, choices=STATUS_CHOICES, verbose_name=_('Статус'),
                                         null=True, blank=True)

    class Meta:
        verbose_name = _('Рейс')
        verbose_name_plural = _('Рейсы')

    def __str__(self):
        if self.numeration:
            return self.numeration
        else:
            return ''


class Box(TimeStampedModel):
    # Коробка
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='box', verbose_name=_('Рейс коробки'),
                               null=True, blank=True)
    code = models.CharField(max_length=64, verbose_name=_('Код'), null=True, blank=True)
    track_code = models.CharField(max_length=64, verbose_name=_('Трек-Код'), null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_('Вес'), null=True, blank=True)
    price = models.CharField(max_length=64, verbose_name=_('Цена'), null=True, blank=True)
    consumption = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_('Расход'), null=True, blank=True)
    sum = models.CharField(max_length=64, verbose_name=_('Сумма'), null=True, blank=True)
    comment = models.TextField(max_length=64, verbose_name=_('comment'), null=True, blank=True)

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
    code = models.CharField(db_index=True, max_length=64, verbose_name=_('Код'))
    track_code = models.CharField(db_index=True, max_length=64, verbose_name=_('Трек-Код'))
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=_('Вес'))

    # Габариты
    width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Ширина'))
    length = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Длина'))
    height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Высота'))

    class Meta:
        verbose_name = _('base_parcel')
        verbose_name_plural = _('base_parcels')

    def __str__(self):
        if self.code:
            return self.code
        else:
            return ''
