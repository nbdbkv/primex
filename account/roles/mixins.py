from account.models import User
from account.roles import courier, operator, subadmin
from account.choices import UserRole
from account.roles.subadmin import UserAdminForm


class ParcelAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        return qs.filter(direction__district__region=user.region)


class UserAdminMixin:

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.role == UserRole.OPERATOR:
            return qs.filter(
                region=user.region, role__in=[UserRole.CLIENT, UserRole.COURIER]
            )
        elif user.role == UserRole.SUBADMIN:
            return qs.filter(region=user.region)
        elif user.role == UserRole.COURIER:
            return qs.filter(id__in=user.parcels.values_list("id", flat=True))
        return qs

    def get_form(self, request, obj=None, **kwargs):
        if request.user.role == UserRole.OPERATOR:
            kwargs["form"] = operator.UserAdminForm
            kwargs["form"].base_fields["region"].initial = request.user.region.id
        elif request.user.role == UserRole.SUBADMIN:
            kwargs["form"] = subadmin.UserAdminForm
        return super().get_form(request, obj,  **kwargs)

