from django.forms import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from operation.models import Parcel

import hashlib


class CashReceivingSerializer(serializers.Serializer):
    amount = serializers.DecimalField(required=True, max_digits=9, decimal_places=2)
    operation_id = serializers.CharField(required=True)
    parcel_code = serializers.SlugField(required=True)
    sha1_hash = serializers.CharField(required=True)

    def validate_parcel_code(self, parcel_code):
        try:
            Parcel.objects.get(code=parcel_code)
            return parcel_code
        except Parcel.DoesNotExist:
            raise ValidationError(message=_("Parcel does not exist"))

    def validate(self, attrs: dict) -> dict:
        sha1_hash = attrs.pop("sha1_hash")
        attrs["secret"] = settings.CASHBOX_SECRET

        data = [i[1] for i in sorted(attrs.items())]
        obj_str = "&".join(map(str, data))
        hash1 = hashlib.sha1(bytes(obj_str, "utf-8"))
        pbhash = hash1.hexdigest()
        if sha1_hash == pbhash:
            attrs["sha1_hash"] = sha1_hash
            return attrs
        raise ValidationError(message=_("Hash sums do not match"))
