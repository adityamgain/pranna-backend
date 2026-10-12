from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start', 'end', 'all_day', 'location',
                    'spots_left', 'is_featured', 'is_published']
    list_filter = ['event_type', 'is_published', 'is_featured', 'all_day', 'destination', 'start']
    list_editable = ['is_featured', 'is_published']
    search_fields = ['title', 'short_description', 'description', 'location']
    date_hierarchy = 'start'
    readonly_fields = ['slug', 'created_at', 'updated_at']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'event_type', 'icon', 'short_description', 'description')}),
        ('Schedule', {'fields': ('start', 'end', 'all_day')}),
        ('Location & Related', {'fields': ('location', 'destination', 'journey', 'package')}),
        ('Pricing & Capacity', {'fields': ('price', 'price_display', 'capacity', 'spots_left',
                                           'registration_url')}),
        ('Appearance', {'fields': ('featured_image', 'color_hex', 'is_featured', 'is_published')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
