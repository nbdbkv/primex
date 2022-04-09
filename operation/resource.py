from import_export import resources
from import_export.fields import Field
from django.utils.translation import gettext_lazy as _

from .models import Parcel, Direction, UserInfo, ParcelOption


class ParcelResource(resources.ModelResource):
    id = Field(attribute="pk", column_name="id")
    title = Field(attribute="title", column_name=_("title"))
    sender__info = Field(attribute="sender", column_name=_("sender"))
    recipient = Field(column_name=_("recipient"))
    status = Field(attribute="status__title", column_name=_("status"))
    code = Field(attribute="code", column_name=_("code"))
    create_at = Field(attribute="create_at", column_name=_("create at"))
    option = Field(attribute="option__type", column_name=_("option"))
    sending_date = Field(attribute="sending_date", column_name=_("sending date"))
    payment_price = Field(attribute="payment__price", column_name=_("price"))
    delivery_type = Field(
        attribute="payment__delivery_type", column_name=_("delivery type")
    )
    pay_status = Field(attribute="payment__pay_status", column_name=_("pay status"))
    envelop = Field(attribute="payment__envelop", column_name=_("envelop"))

    # Direction
    from_to = Field(column_name=_("from region"))
    to_region = Field(column_name=_("to region"))

    class Meta:
        model = Parcel
        exclude = ("sender",)

    def get_name(self, direction):
        return direction.district.name

    def dehydrate_from_to(self, parsel):
        direction = self.get_name(Direction.objects.get(parcel=parsel, type=1))
        return "%s" % direction

    def dehydrate_to_region(self, parsel):
        direction = self.get_name(Direction.objects.get(parcel=parsel, type=2))
        return "%s" % direction

    def dehydrate_recipient(self, parcel):
        recipient = UserInfo.objects.get(parcel=parcel, type=2)
        return "%s" % recipient.info

    def dehydrate_option(self, parcel):
        options = parcel.option.values()
        ran = parcel.option.values().count()
        ans = ""
        for option in range(ran):
            ans += str(options[option]["title"])
            if ran > 1:
                ans += ", "
        return "%s" % ans
