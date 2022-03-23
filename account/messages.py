from enum import Enum
from django.utils.translation import gettext_lazy as _


class Message(Enum):
    USER_ACTIVATED = {"message": _("User is activated")}
    PASSWORD_CHANGED = {"message": _("Password successfully changed")}
    PHONE_CHANGED = {"message": _("Phone successfully changed")}
    CODE_SENT = {"message": _("The code was successfully sent")}


class ErrorMessage(Enum):
    USER_NOT_EXISTS = {"message": _("A user with that phone number does not exists.")}
    WRONG_OTP = {"message": _("Wrong otp code")}
    PASSWORD_VALID = {"message": _("provide a strong password!")}
