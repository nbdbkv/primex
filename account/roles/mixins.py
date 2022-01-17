import imp
from account.roles import courier, operator, subadmin
from account.choices import UserRole


class UserAdminMixin:

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.role == UserRole.OPERATOR:
            return qs.filter(region=user.region, role__in=[UserRole.CLIENT, UserRole.COURIER])
        elif user.role == UserRole.SUBADMIN:
            return qs.filter(role__in=[UserRole.CLIENT, UserRole.COURIER, UserRole.OPERATOR])
        return qs
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.role == UserRole.OPERATOR:
            kwargs['form'] = operator.UserAdminForm
            kwargs['form'].base_fields['region'].initial = request.user.region
        elif request.user.role == UserRole.SUBADMIN:
            kwargs['form'] = subadmin.UserAdminForm
        return super().get_form(request, obj, **kwargs)
    
    def has_module_permission(self, request) -> bool:
        if request.user.is_anonymous:
            return super().has_module_permission(request)
        elif request.user.role == UserRole.COURIER:
            return True
        return super().has_module_permission(request)
