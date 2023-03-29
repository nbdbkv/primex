from django.contrib import admin
from django_2gis_maps.admin import DoubleGisAdmin
from django.utils.translation import gettext_lazy as _
from account.roles.mixins import UserAdminMixin
from account.models import User, Region, District, Village

admin.site.site_header = _("Администрация 9999")


@admin.register(User)
class UserAdmin(UserAdminMixin, admin.ModelAdmin):
    list_display = ('code_logistic', 'first_name', 'last_name', 'phone', 'region')
    list_display_links = ('code_logistic', 'first_name', 'last_name', 'phone', 'region')
    # list_filter = ('role', 'region')
    search_fields = ['code_logistic', 'first_name', 'last_name', 'phone']

    def save_model(self, request, obj, form, change) -> None:
        new_password = form.data["password"]
        if not change or self.get_object(request, obj.id).password != new_password:
            obj.set_password(new_password)
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.GET.get('q'):
            qs = self.model._default_manager.get_queryset()
            ordering = self.get_ordering(request)
            if ordering:
                qs = qs.order_by(*ordering)
            return qs
        else:
            return self.model.objects.none()


class RegionAdmin(DoubleGisAdmin):
    multiple_markers = False
    list_display = ('name', 'position')
    list_editable = ('position',)


class DistrictAdmin(DoubleGisAdmin):
    list_display = ('name', 'code', 'region_code')
    list_filter = ('region',)
    multiple_markers = False

    @admin.display(description=_("region"))
    def region_code(self, obj):
        return obj.region.code


class VillageAdmin(DoubleGisAdmin):
    multiple_markers = False


admin.site.register(Region, RegionAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Village, VillageAdmin)
