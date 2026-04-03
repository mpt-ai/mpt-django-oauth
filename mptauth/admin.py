from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from . import models

class RoleFilter(admin.SimpleListFilter):
    title = _('role')
    parameter_name = 'role'

    def get_roles(self):
        qs = models.Account.objects.all().values('role')
        roles = set([obj.get('name') for elm in qs for obj in elm.get('role')])
        return roles

    def lookups(self, request, model_admin):
        roles = self.get_roles()
        return (
            (role, _(role))
            for role in roles
        )

    def queryset(self, request, queryset):
        if self.value() in self.get_roles():
            return queryset.filter(role__contains=[{'name': self.value()}])
        return queryset

class AccountAdmin(admin.ModelAdmin):
    list_display = [f.name for f in models.Account._meta.fields] + ['is_staff', 'is_supseruser']
    search_fields = ['user__username', 'first_name', 'last_name', 'email']
    list_filter = [RoleFilter, 'user__is_staff', 'user__is_superuser']

    def is_staff(self, obj):
        return obj.user.is_staff
    is_staff.boolean = True
    is_staff.short_description = 'Staff'

    def is_supseruser(self, obj):
        return obj.user.is_superuser
    is_supseruser.boolean = True
    is_supseruser.short_description = 'Superuser'

    
admin.site.register(models.Account, AccountAdmin)

class AccessLogAdmin(admin.ModelAdmin):
    list_display = [f.name for f in models.AccessLog._meta.fields]
admin.site.register(models.AccessLog, AccessLogAdmin)