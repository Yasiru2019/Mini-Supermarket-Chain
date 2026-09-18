from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Supermarket role', {'fields': ('role', 'outlet')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Supermarket role', {'fields': ('role', 'outlet')}),
    )
    list_display = ('username', 'email', 'role', 'outlet', 'is_staff')
    list_filter = DjangoUserAdmin.list_filter + ('role', 'outlet')


admin.site.register(User, UserAdmin)
