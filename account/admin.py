from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_2gis_maps.admin import DoubleGisAdmin
from account.roles.mixins import UserAdminMixin
from account.models import User, Region, District, Village


class UserAdmin(UserAdminMixin, admin.ModelAdmin):
    def save_model(self, request, obj, form, change) -> None:
        new_password = form.data["password"]
        if not change or self.get_object(request, obj.id).password != new_password:
            obj.set_password(new_password)
        return super().save_model(request, obj, form, change)



class RegionAdmin(DoubleGisAdmin):
    multiple_markers = False


class DistrictAdmin(DoubleGisAdmin):
    multiple_markers = False


class VillageAdmin(DoubleGisAdmin):
    multiple_markers = False


admin.site.register(User, UserAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Village, VillageAdmin)
