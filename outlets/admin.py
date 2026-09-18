from django.contrib import admin

from .models import Outlet


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'gst_number', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'gst_number')
