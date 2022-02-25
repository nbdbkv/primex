from django.db import models
from django.utils.translation import gettext_lazy as _
from django_2gis_maps import fields as map_fields
from django_2gis_maps.mixins import DoubleGisMixin

from ckeditor_uploader.fields import RichTextUploadingField

from account.models import User, Region, District


class Partner(models.Model):
    name = models.CharField(_('company name'), max_length=100)
    logo = models.ImageField(_('logo'), upload_to='about/partners/')
    
    def __str__(self) -> str:
        return self.name


class Contact(models.Model):
    social = models.CharField(_('social'), max_length=100)
    icon = models.ImageField(_('social icon'), upload_to='about/contacts/')
    
    def __str__(self) -> str:
        return self.social
    

class ArticleCategory(models.Model):
    name = models.CharField(_('name'), max_length=255)
    
    def __str__(self) -> str:
        return self.name
    

class New(models.Model):
    title = models.CharField(_('title'), max_length=255)
    description = RichTextUploadingField()
    border_photo = models.ImageField(_('border image'), upload_to='about/news/')
    category = models.ForeignKey(ArticleCategory, on_delete=models.DO_NOTHING, verbose_name=_('article category'))
    watched_users = models.ManyToManyField(User, verbose_name=_('watched users'), blank=True)
    watched_anonymous_users = models.PositiveIntegerField(_('watched anonymous users'), default=0, blank=True)
    create_at = models.DateTimeField(_('created date'), auto_now_add=True)
    
    def __str__(self) -> str:
        return self.title


class NewGallery(models.Model):
    image = models.ImageField(_('image'), upload_to='about/news/')
    new = models.ForeignKey(New, on_delete=models.CASCADE)


class Fillial(DoubleGisMixin, models.Model):
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    location = map_fields.GeoLocationField(_('geolocation'))
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True)
    email = models.EmailField(_('email'), blank=True)
    
    def __str__(self) -> str:
        return self.district


class Option(models.Model):
    alias = models.CharField(_('alias'), max_length=50, unique=True)
    value = models.IntegerField(_('value'))
    description = models.TextField(_('description'))
    
    def __str__(self) -> str:
        return self.alias
    

class Question(models.Model):
    title = models.CharField(_('title'), max_length=255)
    text = models.TextField(_('text'))
    
    def __str__(self) -> str:
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(Question, verbose_name=_('question'), on_delete=models.CASCADE)
    text = models.TextField(_('text'))
