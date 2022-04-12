from django.db import models
from django.utils.translation import gettext_lazy as _
from django_2gis_maps import fields as map_fields
from django_2gis_maps.mixins import DoubleGisMixin

from ckeditor_uploader.fields import RichTextUploadingField

from account.models import User, Region, District


class Partner(models.Model):
    name = models.CharField(_("company name"), max_length=100)
    logo = models.ImageField(_("logo"), upload_to="about/partners/")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")


class Contact(models.Model):
    social = models.CharField(_("social"), max_length=100)
    icon = models.ImageField(_("social icon"), upload_to="about/contacts/")

    def __str__(self) -> str:
        return self.social

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")


class ArticleCategory(models.Model):
    name = models.CharField(_("name"), max_length=255)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Article category")
        verbose_name_plural = _("Article categories")


class New(models.Model):
    title = models.CharField(_("title"), max_length=255)
    description = RichTextUploadingField()
    border_photo = models.ImageField(_("border image"), upload_to="about/news/")
    category = models.ForeignKey(
        ArticleCategory,
        on_delete=models.SET_NULL,
        verbose_name=_("article category"),
        null=True,
    )
    watched_count = models.PositiveIntegerField(_("watched count"))
    create_at = models.DateTimeField(_("created date"), auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("New")
        verbose_name_plural = _("News")


class NewGallery(models.Model):
    image = models.ImageField(_("image"), upload_to="about/news/")
    new = models.ForeignKey(New, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("New gallery")
        verbose_name_plural = _("New galleries")


class Fillial(DoubleGisMixin, models.Model):
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    location = map_fields.GeoLocationField(_("geolocation"))
    contact_phone = models.CharField(_("contact phone"), max_length=20, blank=True)
    email = models.EmailField(_("email"), blank=True)

    def __str__(self) -> str:
        return self.district

    class Meta:
        verbose_name = _("Fillial")
        verbose_name_plural = _("Fillials")


class Option(models.Model):
    alias = models.CharField(_("alias"), max_length=50, unique=True)
    value = models.IntegerField(_("value"))
    description = models.TextField(_("description"))

    def __str__(self) -> str:
        return self.alias

    class Meta:
        verbose_name = _("Option")
        verbose_name_plural = _("Options")


class Question(models.Model):
    title = models.CharField(_("title"), max_length=255)
    text = models.TextField(_("text"))

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")


class Answer(models.Model):
    question = models.ForeignKey(
        Question, verbose_name=_("question"), on_delete=models.CASCADE
    )
    text = models.TextField(_("text"))

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
