from django.contrib import admin
from .models import MerchandiseCategory


@admin.register(MerchandiseCategory)
class MerchandiseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )