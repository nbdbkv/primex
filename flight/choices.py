from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusChoices(models.IntegerChoices):
    # Статусы
    FORMING = 0, _('Формируется')
    TRANSPORTING = 1, _('В пути')
    ARRIVED = 2, _('Прибыл рейс')
    SORTING = 3, _('Сортируется на складе')
    DISTRIBUTING = 4, _('Готов к выдаче')
    DISTRIBUTED = 5, _('Выдан')
    UNKNOWN = 7, _('Неизвестные заказы')


def get_status():
    statuses = tuple((choice.value, choice.label) for choice in StatusChoices)
    return statuses


class PaymentChoices(models.IntegerChoices):
    # Способы оплаты
    CASH = 0, _('Наличные')
    OPTIMABANK = 1, _('Оптима Банк')
    MBANK = 2, _('MBANK')


def get_payment():
    payments = tuple((choice.value, choice.label) for choice in PaymentChoices)
    return payments
