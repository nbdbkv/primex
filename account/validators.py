from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


PhoneValidator = validators.RegexValidator(
    r"^996\d{9}$",
    message=_(
        "Phone number must be entered in the format: +996*********** Up to 9 digits allowed."
    ),
)


RegionCodeValidator = validators.RegexValidator(
    r"[0-9]{2}", message=_("Code must be 2 digit")
)
