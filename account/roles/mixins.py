from account.models import User
from account.roles import courier, operator, subadmin
from account.choices import UserRole


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
        return qs

    def get_form(self, request, obj=None, **kwargs):
        if request.user.role == UserRole.OPERATOR:
            kwargs["form"] = operator.UserAdminForm
            kwargs["form"].base_fields["region"].initial = request.user.region.id
        elif request.user.role == UserRole.SUBADMIN:
            kwargs["form"] = subadmin.UserAdminForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change) -> None:
        super().save_model(request, obj, form, change)
        if not change:
            group = None
            if obj.role == UserRole.COURIER:
                group = courier.get_group()
            if obj.role == UserRole.OPERATOR:
                group = operator.get_group()
            elif obj.role == UserRole.SUBADMIN:
                group = subadmin.get_group()
            if group:
                obj.groups.add(group)
        return obj
