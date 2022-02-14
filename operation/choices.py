from django.db import models
from django.utils.translation import gettext_lazy as _


class DirectionChoices(models.IntegerChoices):
    FROM = 1, _('from')
    TO = 2, _('to')


class UserInfoChoices(models.IntegerChoices):
    SENDER = 1, _('sender')
    RECIPIENT = 2, _('recipient')
