from django.contrib import admin
from django.utils.html import format_html
from .models import Destination


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_display', 'created_at', 'image_preview']
    list_filter = ['created_at']
    search_fields = ['name', 'short_description', 'description', 'tags']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'image_preview']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'icon', 'short_description', 'description')
        }),
        ('Tags', {
            'fields': ('tags',),
            'classes': ('wide',),
            'description': 'Enter tags as a JSON array: ["meditation", "mountains", "spiritual"]'
        }),
        ('Media', {
            'fields': ('featured_image', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def icon_display(self, obj):
        if obj.icon:
            return format_html('<i class="{}" style="font-size: 1.2rem;"></i>', obj.icon)
        return "-"

    icon_display.short_description = 'Icon'

    def image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px; border-radius: 8px;" />',
                obj.featured_image.url
            )
        return "No image"

    image_preview.short_description = 'Image Preview'

    def save_model(self, request, obj, form, change):
        """Handle JSON field properly"""
        if obj.tags and isinstance(obj.tags, str):
            import json
            try:
                obj.tags = json.loads(obj.tags)
            except:
                obj.tags = [obj.tags]
        super().save_model(request, obj, form, change)
