from django.contrib import admin
from .models import Package

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'level', 'price_display', 'duration_display',
        'in_stock', 'spots_left', 'is_featured', 'created_at'
    ]
    list_filter = ['level', 'in_stock', 'is_featured', 'locations', 'services']
    search_fields = ['name', 'short_description', 'description']
    list_editable = ['in_stock', 'spots_left', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['locations', 'services']  # Nice UI for ManyToMany fields

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'icon', 'short_description', 'description')
        }),
        ('Relationships', {
            'fields': ('locations', 'services')
        }),
        ('Pricing & Availability', {
            'fields': (
                'price_min', 'price_max', 'price_display',
                'in_stock', 'spots_left', 'next_start_date'
            )
        }),
        ('Duration & Level', {
            'fields': ('duration_days', 'duration_display', 'level')
        }),
        ('Features', {
            'fields': ('quick_facts', 'savings_text')
        }),
        ('Media & Appearance', {
            'fields': ('featured_image', 'color_hex', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )