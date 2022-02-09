from django.db import models
from django.utils.translation import gettext_lazy as _
from django_2gis_maps import fields
from django_2gis_maps.mixins import DoubleGisMixin
from account.models import City, User, Region, District
from account.validators import PhoneValidator


class DeliveryStatus(models.Model):
    title = models.CharField(_('title'), max_length=100)

class ParcelOption(models.Model):
    title = models.CharField(_('option title'), max_length=255)

class Parcel(models.Model):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_('sender'))
    status = models.ForeignKey(DeliveryStatus, on_delete=models.SET_NULL, verbose_name=_('delivery status'), null=True)
    code = models.CharField(_('code'), max_length=15)
    create_at = models.DateTimeField(_('date creation'), auto_now_add=True)
    option = models.ManyToManyField(ParcelOption, verbose_name=_('options'))
    sending_date = models.DateTimeField(_('sendin date'))
    

class DeliveryType(models.Model):
    icon = models.ImageField(_('icon'), upload_to='project/')
    image = models.ImageField(_('image'), upload_to='project/')
    title = models.CharField(_('title'), max_length=255)
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)


class Packaging(models.Model):
    title = models.CharField(_('title'), max_length=255)
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    quantity = models.PositiveIntegerField(_('quantity'), default=0),
    unit = models.CharField(_('measuring unit'), max_length=20)

class PayStatus(models.Model):
    title = models.CharField(_('status title'), max_length=50)

class PriceList(models.Model):
    from_region = models.ForeignKey(Region, on_delete=models.SET_NULL, verbose_name=_('from region'), null=True)
    to_district = models.ForeignKey(City, on_delete=models.SET_NULL, verbose_name=_('to district'), null=True)
    kilo = models.PositiveSmallIntegerField(_('kilo price'))
    delivery_time = models.FloatField(_('delivery time in hours'))


class Envelop(models.Model):
    title = models.CharField(_('envelop title'), max_length=100)


class PriceEnvelop(models.Model):
    from_region = models.ForeignKey(Region, on_delete=models.SET_NULL, verbose_name=_('from region'), null=True)
    to_district = models.ForeignKey(City, on_delete=models.SET_NULL, verbose_name=_('to district'), null=True)
    price = models.DecimalField(_('price'), max_digits=6, decimal_places=2)
    envelop = models.ForeignKey(Envelop, on_delete=models.SET_NULL, verbose_name=_('envelop'), null=True)
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, verbose_name=_('price list'))


class PaymentDimension(models.Model):
    length = models.FloatField(_('parcel length'))
    width = models.FloatField(_('parcel width'))
    height = models.FloatField(_('parcel height'))
    weight = models.FloatField(_('parcel weight'))


class DimensionPrice(models.Model):
    from_region = models.ForeignKey(Region, on_delete=models.SET_NULL, verbose_name=_('from region'), null=True)
    to_district = models.ForeignKey(City, on_delete=models.SET_NULL, verbose_name=_('to district'), null=True)
    price = models.DecimalField(_('price'), max_digits=6, decimal_places=2)
    dimension = models.ForeignKey(PaymentDimension, on_delete=models.SET_NULL, verbose_name=_('dimension'), null=True)
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, verbose_name=_('price list'))


class ParcelPayment(models.Model):
    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE, verbose_name=_('parcel'))
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.SET_NULL, null=True, verbose_name=_('delivery type'))
    packaging = models.ManyToManyField(Packaging, verbose_name=_('parcel packaging'))
    pay_status = models.ForeignKey(PayStatus, on_delete=models.SET_NULL, null=True, verbose_name=_('pay status'))
    price_list = models.ForeignKey(PriceList, on_delete=models.SET_NULL, verbose_name=_('price list'), null=True)

class PaymentType(models.Model):
    title = models.CharField(_('title'), max_length=100)


class Payment(models.Model):
    parcel = models.ForeignKey(ParcelPayment, on_delete=models.CASCADE, verbose_name=_('parcel payment'))
    type = models.ForeignKey(PaymentType, on_delete=models.SET_NULL, verbose_name=_('type'), null=True)
    sum = models.DecimalField(_('sum'), max_digits=9, decimal_places=2)

class Direction(DoubleGisMixin, models.Model):
    TYPE = (
        (1, 'from'),
        (2, 'to')
    )
    
    type = models.PositiveSmallIntegerField(_('type'), choices=TYPE)
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, verbose_name=_('parcel'))
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, verbose_name=_('city'), blank=True)
    district = models.ForeignKey(District, on_delete=models.DO_NOTHING, verbose_name=_('district'), blank=True)
    geolocation = fields.GeoLocationField(_('geolocation'), blank=True)


class UserInfo(models.Model):
    TYPE = (
        (1, 'sender'),
        (2, 'recipient')
    )
    
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, verbose_name=_('parcel'))
    phone = models.CharField(_('phone'), max_length=15, validators=[PhoneValidator])
    info = models.CharField(_('user info'), max_length=255, blank=True)
    zip_code = models.CharField(_('zip code'), max_length=15, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, verbose_name='user account')
    type = models.PositiveSmallIntegerField(_('user info type'), choices=TYPE)
    

class ParcelDimension(models.Model):
    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE, verbose_name=_('parcel'))
    length = models.FloatField(_('parcel length'))
    width = models.FloatField(_('parcel width'))
    height = models.FloatField(_('parcel height'))
    weight = models.FloatField(_('parcel weight'))
