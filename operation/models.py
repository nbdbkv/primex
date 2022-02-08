from django.db import models
from django.utils.translation import gettext_lazy as _
from django_2gis_maps import fields
from django_2gis_maps.mixins import DoubleGisMixin

from account.models import City, User, Region, District
from account.validators import PhoneValidator


class UserInfo(models.Model):
    phone = models.CharField(_('phone'), max_length=15, validators=[PhoneValidator])
    info = models.CharField(_('user info'), max_length=255, blank=True)
    zip_code = models.CharField(_('zip code'), max_length=15, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, verbose_name='user account')
    
    
class ParcelDimension(models.Model):
    length = models.FloatField(_('parcel length'))
    width = models.FloatField(_('parcel width'))
    height = models.FloatField(_('parcel height'))
    weight = models.FloatField(_('parcel weight'))


class ParcelOptions(models.Model):
    title = models.CharField(_('option title'), max_length=255)


class Direction(DoubleGisMixin, models.Model):
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, verbose_name=_('city'), blank=True)
    district = models.ForeignKey(District, on_delete=models.DO_NOTHING, verbose_name=_('district'), blank=True)
    geolocation = fields.GeoLocationField(_('geolocation'), blank=True)


class ParcelInfo(models.Model):
    parcel = models.OneToOneField('Parcel', on_delete=models.CASCADE, verbose_name=_('parcel'))
    sender_info = models.ForeignKey(UserInfo, on_delete=models.DO_NOTHING, verbose_name=_('sender info'), related_name='sender_info')
    recipient_info = models.ForeignKey(UserInfo, on_delete=models.DO_NOTHING, verbose_name=_('recipient info'), related_name='recipient_info')
    dimension = models.ForeignKey(ParcelDimension, on_delete=models.DO_NOTHING, verbose_name=_('parcel dimension'))
    options = models.ManyToManyField(ParcelOptions, verbose_name=_('options'))
    location_from = models.ForeignKey(Direction, on_delete=models.DO_NOTHING, verbose_name=_('location from'), related_name='location_from')
    location_to = models.ForeignKey(Direction, on_delete=models.DO_NOTHING, verbose_name=_('location to'), related_name='location_to')
    

class DeliveryType(models.Model):
    title = models.CharField(_('title'), max_length=255)
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)


class Packaging(models.Model):
    title = models.CharField(_('title'), max_length=255)
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    quantity = models.PositiveIntegerField(_('quantity'), default=0),
    unit = models.CharField(_('measuring unit'), max_length=20)


class PayStatus(models.Model):
    title = models.CharField(_('status title'), max_length=50)
    

class PaymentType(models.Model):
    title = models.CharField(_('title'), max_length=100)


class Payment(models.Model):
    type = models.ForeignKey(PaymentType, on_delete=models.SET_NULL, verbose_name=_('type'), null=True)
    sum = models.DecimalField(_('sum'), max_digits=9, decimal_places=2)


class ParcelEnvelop(models.Model):
    title = models.CharField(_('envelop title'), max_length=100)
    price = models.DecimalField(_('price'), max_digits=6, decimal_places=2)


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


class PriceList(models.Model):
    from_region = models.ForeignKey(Region, on_delete=models.SET_NULL, verbose_name=_('from region'), null=True)
    to_district = models.ForeignKey(City, on_delete=models.SET_NULL, verbose_name=_('to district'), null=True)
    envelop = models.ForeignKey(ParcelEnvelop, on_delete=models.SET_NULL, verbose_name=_('envelop'), null=True)
    dimension_price = models.ForeignKey(DimensionPrice, on_delete=models.SET_NULL, verbose_name=_('dimension'), null=True)
    kilo = models.PositiveSmallIntegerField(_('kilo price'))
    delivery_time = models.FloatField(_('delivery time in hours'))
    

class ParcelPayment(models.Model):
    parcel = models.OneToOneField('Parcel', on_delete=models.CASCADE, verbose_name=_('parcel'))
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.SET_NULL, null=True, verbose_name=_('delivery type'))
    packaging = models.ForeignKey(Packaging, on_delete=models.SET_NULL, null=True, verbose_name=_('parcel packaging'))
    pay_status = models.ForeignKey(PayStatus, on_delete=models.SET_NULL, null=True, verbose_name=_('pay status'))
    payment = models.ManyToManyField(Payment, verbose_name=_('payment'))
    price_list = models.ForeignKey(PriceList, on_delete=models.SET_NULL, verbose_name=_('price list'), null=True)


class DeliveryStatus(models.Model):
    title = models.CharField(_('title'), max_length=100)


class Parcel(models.Model):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_('sender'))
    status = models.ForeignKey(DeliveryStatus, on_delete=models.SET_NULL, verbose_name=_('delivery status'), null=True)
    code = models.CharField(_('code'), max_length=15)
    create_at = models.DateTimeField(_('date creation'), auto_now_add=True)
