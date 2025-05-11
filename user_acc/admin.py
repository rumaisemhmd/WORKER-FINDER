from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Users
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    model = Users
    list_display = ('email', 'first_name', 'last_name', 'state', 'district', 'mobile', 'is_staff', 'is_active')
    list_filter = ('state', 'district', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'mobile')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'mobile', 'state', 'district')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'mobile', 'state', 'district', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )


admin.site.register(Users, UserAdmin)