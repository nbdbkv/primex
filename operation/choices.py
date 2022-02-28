from django.db import models
from django.utils.translation import gettext_lazy as _


class DirectionChoices(models.IntegerChoices):
    FROM = 1, _('from')
    TO = 2, _('to')


class UserInfoChoices(models.IntegerChoices):
    SENDER = 1, _('sender')
    RECIPIENT = 2, _('recipient')


class PayStatusChoices(models.TextChoices):
    IN_ANTICIPATION = 'in_anticipation', _('in anticipation')
    PAID = 'paid', _('paid')


class PaymentTypeChoices(models.TextChoices):
    CASH = 'cash', _('cash')
    BONUS = 'bonus', _('bonus')


class PaymentHistoryType(models.IntegerChoices):
    CREDIT = 1, _('credit')
    DEBIT = 2, _('debit')
