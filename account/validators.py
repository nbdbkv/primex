from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PhoneValidator(validators.RegexValidator):
    regex = r'^996\d{9}$'
    message = _(
        'Phone number must be entered in the format: +996*********** Up to 9 digits allowed.'
    )
    flags = 0
