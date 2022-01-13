from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentHistoryType(models.IntegerChoices):
    CREDIT = 1, _('credit')
    DEBIT = 2, _('debit')


class SendCodeType(models.IntegerChoices):
    REGISTER = 1, _('register')
    RESET_PASSWORD = 2, _('reset password')
