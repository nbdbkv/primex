from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(db_index=True, auto_now=True, verbose_name=_('Дата изменения'))

    class Meta:
        abstract = True


class Flight(TimeStampedModel):
    '''Рейс'''
    numeration = models.CharField(db_index=True, max_length=64, verbose_name=_('Нумерация рейсов'))
    code = models.CharField(db_index=True, max_length=64, verbose_name=_('Код'), unique=True)
    quantity = models.PositiveIntegerField(verbose_name=_('Количество мест (коробка)'))

    class TranslatableMeta:
        fields = ['numeration', 'code', 'quantity', 'created_at', 'updated_at']

    class Meta:
        verbose_name = _('flight')
        verbose_name_plural = _('flights')

# class Box(TimeStampedModel):
#     flight = models.
#
#
# class BaseParcel(TimeStampedModel):
#     pass
