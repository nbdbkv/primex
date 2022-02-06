from account.models import User
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
            kwargs['form'].base_fields['region'].initial = request.user.region.id
        elif request.user.role == UserRole.SUBADMIN:
            kwargs['form'] = subadmin.UserAdminForm
        return super().get_form(request, obj, **kwargs)
    
    # def save_model(self, request, obj, form, change) -> None:
    #     super().save_model(request, obj, form, change)
    #     if obj.role == UserRole.OPERATOR:
    #         perm = operator.get_permission()
    #     elif obj.role == UserRole.SUBADMIN:
    #         perm = subadmin.get_permission()
    #     for permission in perm:
    #         obj.user_permissions.through.objects.create(user_id=obj.id, permission_id=permission.id)
    #     print(obj.get_all_permissions())
    #     return obj

    
    # def save_form(self, request, form, change):
    #     form.data._mutable = True
    #     form.data['points'] = 24
    #     form.data._mutable = False
    #     print(form.data, request.POST, sep='\n')
    #     form.save()
    #     return super().save_form(request, form, change)
