from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django_2gis_maps import fields as map_fields
from django_2gis_maps.mixins import DoubleGisMixin
from rest_framework_simplejwt.tokens import RefreshToken
from solo.models import SingletonModel

from account.validators import PhoneValidator, RegionCodeValidator
from account.managers import UserManager
from account.choices import UserRole


class User(AbstractUser):
    phone_validator = PhoneValidator

    phone = models.CharField(
        _("user phone number"),
        max_length=15,
        unique=True,
        help_text=_('Required. 9 digits in format: 996*********** without "+".'),
        validators=[phone_validator],
        error_messages={
            "unique": _("A user with that phone number already exists."),
        },
    )
    code_logistic = models.CharField(verbose_name=_("Код логистики"), max_length=200, null=True, blank=True)
    qr_phone = models.ImageField(
        verbose_name=_("QR-Код телефона"), upload_to='account/user/qrcode/phone', null=True, blank=True,
    )
    qr_logistic = models.ImageField(
        verbose_name=_("QR-Код логистики"), upload_to='account/user/qrcode/logistic', null=True, blank=True,
    )
    info = models.CharField(_("user info"), max_length=255)
    region = models.ForeignKey(
        "Region", on_delete=models.SET_NULL, verbose_name=_("region"), null=True, blank=True,
    )
    district = models.ForeignKey(
        "District", on_delete=models.SET_NULL, verbose_name=_("district"), null=True, blank=True
    )
    role = models.PositiveSmallIntegerField(
        _("role"), choices=UserRole.choices, default=UserRole.CLIENT
    )
    points = models.PositiveIntegerField(_("user bonus points"), default=50)
    avatar = models.ImageField(_("avatar"), upload_to="user/", blank=True)
    tg_chat_id = models.CharField(
        _("telegram chat id"), max_length=20, blank=True, null=True
    )
    tg_user_id = models.CharField(
        _("telegram user id"), max_length=20, blank=True, null=True
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    send_code = models.CharField(null=True, blank=True, max_length=8)
    verify_date = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.phone

    username = None
    email = None

    objects = UserManager()

    EMAIL_FIELD = None
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "phone"

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class Region(DoubleGisMixin, models.Model):
    name = map_fields.AddressField(_("name"), max_length=100)
    geolocation = map_fields.GeoLocationField(_("geolocation"), blank=True)
    code = models.CharField(_("code"), max_length=4, validators=[RegionCodeValidator])
    position = models.PositiveSmallIntegerField(_('position'), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")


class District(DoubleGisMixin, models.Model):
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, verbose_name=_("region")
    )
    name = map_fields.AddressField(_("name"), max_length=100)
    geolocation = map_fields.GeoLocationField(_("geolocation"), blank=True)
    code = models.CharField(_("code"), max_length=4, validators=[RegionCodeValidator])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("District")
        verbose_name_plural = _("Districts")


class Village(models.Model):
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, verbose_name=_("region"), null=True
    )
    name = map_fields.AddressField(_("name"), max_length=100, blank=True)
    geolocation = map_fields.GeoLocationField(_("geolocation"), blank=True)
    code = models.CharField(_("code"), max_length=4, validators=[RegionCodeValidator])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Village")
        verbose_name_plural = _("Villages")


class MobileCode(models.Model):
    operator = models.CharField(verbose_name='Оператор', max_length=3)

    def __str__(self):
        return f'{self.operator}'

    class Meta:
        verbose_name = 'Мобильный оператор'
        verbose_name_plural = verbose_name


class AppVersion(SingletonModel):
    android_version = models.CharField(max_length=32, null=True, blank=True, verbose_name='Android версия',)
    android_is_updated = models.BooleanField(default=False, verbose_name=_('Android версия обновлена'))
    ios_version = models.CharField(max_length=32, null=True, blank=True, verbose_name='iOS версия',)
    ios_is_updated = models.BooleanField(default=False, verbose_name=_('iOS версия обновлена'))

    def __str__(self):
        return self.android_version

    class Meta:
        verbose_name = _('версию приложения')
        verbose_name_plural = _('Версии приложения')
