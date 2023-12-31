from django.contrib import admin
from django_2gis_maps.admin import DoubleGisAdmin
from django.utils.translation import gettext_lazy as _
from account.roles.mixins import UserAdminMixin
from account.models import User, Region, District, Village, MobileCode, AppVersion
from django.contrib.auth.forms import UserChangeForm


@admin.register(User)
class UserAdmin(UserAdminMixin, admin.ModelAdmin):
    list_display = ('code_logistic', 'first_name', 'last_name', 'info', 'phone', 'region', 'date_joined')
    list_display_links = ('code_logistic', 'first_name', 'last_name', 'info', 'phone', 'region')
    # list_filter = ('role', 'region')
    search_fields = ['code_logistic', 'first_name', 'last_name', 'phone']
    # change_list_template = 'admin/user_change_list.html'
    form = UserChangeForm

    def save_model(self, request, obj, form, change) -> None:
        new_password = form.data.get("password")
        if new_password and (not change or self.get_object(request, obj.id).password != new_password):
            obj.set_password(new_password)
        return super().save_model(request, obj, form, change)

    # def changelist_view(self, request, extra_context=None):
    #     extra_context = extra_context or {}
    #     if request.GET.get('q'):
    #         extra_context['is_search'] = True
    #     else:
    #         extra_context['is_search'] = False
    #     return super(UserAdmin, self).changelist_view(request, extra_context=extra_context)


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


@admin.register(MobileCode)
class MobileCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'operator')
    list_display_links = list_display


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('android_version', 'android_is_updated', 'ios_version', 'ios_is_updated')
    list_display_links = list_display


admin.site.register(Region, RegionAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Village, VillageAdmin)
