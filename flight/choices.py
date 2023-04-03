from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusChoices(models.IntegerChoices):
    # Статусы
    FORMING = 0, _('Формируется')
    TRANSPORTING = 1, _('В пути')
    ARRIVED = 2, _('Прибыл')
    SORTING = 3, _('Сортируется')
    DISTRIBUTING = 4, _('Раздается')
    DISTRIBUTED = 5, _('Роздан')


def get_status():
    statuses = tuple((choice.value, choice.label) for choice in StatusChoices)
    return statuses
