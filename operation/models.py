from django.db import models
from django.utils.translation import gettext_lazy as _
from django_2gis_maps import fields
from django_2gis_maps.mixins import DoubleGisMixin
from account.models import District, User, Region, Village
from account.validators import PhoneValidator
from operation.choices import DirectionChoices, PayStatusChoices, UserInfoChoices


class DeliveryStatus(models.Model):
    title = models.CharField(_('title'), max_length=100)
    
    def __str__(self) -> str:
        return self.title


class ParcelOption(models.Model):
    title = models.CharField(_('option title'), max_length=255)
    
    def __str__(self) -> str:
        return self.title


class Parcel(models.Model):
    title = models.CharField(_('title'), max_length=255, blank=True)
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_('sender'))
    status = models.ForeignKey(DeliveryStatus, on_delete=models.SET_NULL, verbose_name=_('delivery status'), null=True)
    code = models.CharField(_('code'), max_length=15)
    create_at = models.DateTimeField(_('date creation'), auto_now_add=True)
    option = models.ManyToManyField(ParcelOption, verbose_name=_('options'))
    sending_date = models.DateTimeField(_('sendin date'))
    
    def __str__(self) -> str:
        return self.title


class Distance(models.Model):
    from_region = models.ForeignKey(Region, on_delete=models.SET_NULL, verbose_name=_('from region'), null=True)
    to_district = models.ForeignKey(District, on_delete=models.SET_NULL, verbose_name=_('to district'), null=True)
    
    def __str__(self) -> str:
        return f'{self.from_region} - {self.to_district}'
    

class DeliveryType(models.Model):
    distance = models.ForeignKey(Distance, on_delete=models.SET_NULL, verbose_name=_('distance'), null=True)
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    delivery_time = models.PositiveIntegerField(_('time in hour'))
    icon = models.FileField(_('icon'), upload_to='project/')
    image = models.ImageField(_('image'), upload_to='project/')
    
    def __str__(self) -> str:
        return self.title


class Packaging(models.Model):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    quantity = models.PositiveIntegerField(_('quantity'), default=0)
    unit = models.CharField(_('measuring unit'), max_length=20)
    
    def __str__(self) -> str:
        return self.title


class PaymentDimension(models.Model):
    length = models.FloatField(_('parcel length'))
    width = models.FloatField(_('parcel width'))
    height = models.FloatField(_('parcel height'))
    weight = models.FloatField(_('parcel weight'))


class Envelop(models.Model):
    distance = models.ForeignKey(Distance, on_delete=models.SET_NULL, verbose_name=_('distance'), null=True)
    price = models.DecimalField(_('price'), max_digits=6, decimal_places=2)
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))
    dimension = models.ForeignKey(PaymentDimension, on_delete=models.SET_NULL, verbose_name=_('dimension'), null=True)
    kilo = models.PositiveIntegerField(_('price per kilo'))
    
    def __str__(self) -> str:
        return self.title


class ParcelPayment(models.Model):
    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE, verbose_name=_('parcel'), related_name='payment')
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2, blank=True, null=True)
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.SET_NULL, null=True, verbose_name=_('delivery type'))
    packaging = models.ManyToManyField(Packaging, verbose_name=_('parcel packaging'))
    pay_status = models.CharField(_('status'), choices=PayStatusChoices.choices, max_length=20, default=PayStatusChoices.IN_ANTICIPATION)
    envelop = models.ForeignKey(Envelop, on_delete=models.SET_NULL, verbose_name=_('envelop'), null=True, blank=True)
    
    def __str__(self) -> str:
        return self.parcel.title


class PaymentType(models.Model):
    icon = models.FileField(_('icon'), upload_to='project/')
    title = models.CharField(_('title'), max_length=100)
    
    def __str__(self) -> str:
        return self.title


class Payment(models.Model):
    parcel = models.ForeignKey(ParcelPayment, on_delete=models.CASCADE, verbose_name=_('parcel payment'), related_name='payment')
    type = models.ForeignKey(PaymentType, on_delete=models.SET_NULL, verbose_name=_('type'), null=True)
    sum = models.DecimalField(_('sum'), max_digits=9, decimal_places=2)
    
    def __str__(self) -> str:
        return self.parcel.parcel.title


class Direction(DoubleGisMixin, models.Model):
    type = models.PositiveSmallIntegerField(_('type'), choices=DirectionChoices.choices)
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, verbose_name=_('parcel'), related_name='direction')
    district = models.ForeignKey(District, on_delete=models.DO_NOTHING, verbose_name=_('district'), blank=True)
    village = models.ForeignKey(Village, on_delete=models.DO_NOTHING, verbose_name=_('village'), blank=True)
    destination = models.CharField(_('destination'), max_length=255, blank=True)
    geolocation = fields.GeoLocationField(_('geolocation'), blank=True)
    
    def __str__(self) -> str:
        return f'{self.type} -> {self.parcel.title}'
    
    class Meta:
        ordering = ['type']


class UserInfo(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, verbose_name=_('parcel'), related_name='user_info')
    phone = models.CharField(_('phone'), max_length=15, validators=[PhoneValidator])
    info = models.CharField(_('user info'), max_length=255, blank=True)
    company = models.CharField(_('company'), max_length=50, blank=True)
    email = models.EmailField(_('email'), blank=True)
    type = models.PositiveSmallIntegerField(_('user info type'), choices=UserInfoChoices.choices)
    
    def __str__(self) -> str:
        return f'{self.type} -> {self.parcel.title}'
    
    class Meta:
        ordering = ['type']
    

class ParcelDimension(models.Model):
    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE, verbose_name=_('parcel'), related_name='dimension')
    length = models.FloatField(_('parcel length'))
    width = models.FloatField(_('parcel width'))
    height = models.FloatField(_('parcel height'))
    weight = models.FloatField(_('parcel weight'))
    
    def __str__(self) -> str:
        return self.parcel.title
