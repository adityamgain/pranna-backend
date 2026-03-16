from django.contrib import admin
from django.utils.html import format_html
from .models import (
    GalleryCategory, GalleryImage, GalleryAlbum,
    GalleryTag, GalleryImageTag, GalleryImageJourney
)


class GalleryImageJourneyInline(admin.TabularInline):
    """
    Inline admin for managing journey relationships directly in the image admin
    """
    model = GalleryImageJourney
    extra = 3  # Show 3 empty forms by default
    verbose_name = "Associated Journey"
    verbose_name_plural = "Associated Journeys"
    fields = ['journey', 'is_primary', 'caption', 'order']
    autocomplete_fields = ['journey']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Optimize the journey dropdown"""
        if db_field.name == "journey":
            kwargs["queryset"] = db_field.remote_field.model.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class GalleryImageTagInline(admin.TabularInline):
    model = GalleryImageTag
    extra = 1
    autocomplete_fields = ['tag']


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'order']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'icon')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Status', {
            'fields': ('is_active', 'order', 'created_at', 'updated_at')
        }),
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'title', 'category', 'location', 'journeys_count', 'is_featured', 'is_active', 'order']
    list_filter = ['category', 'is_featured', 'is_active', 'location', 'image_journeys__journey']
    search_fields = ['title', 'description', 'caption', 'location']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured', 'is_active', 'order']
    readonly_fields = ['created_at', 'updated_at', 'thumbnail_preview', 'journeys_list_display']

    # Use inlines instead of filter_horizontal
    inlines = [GalleryImageJourneyInline, GalleryImageTagInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'caption', 'alt_text')
        }),
        ('Media', {
            'fields': ('image', 'thumbnail_preview', 'high_res_image')
        }),
        ('Categorization', {
            'fields': ('category', 'location', 'date_taken', 'photographer')
        }),
        ('Journey Association', {
            'fields': ('journeys_list_display',),
            'description': 'Use the table below to associate this image with journeys. Click "Add another Associated Journey" to add more.',
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active', 'order', 'created_at', 'updated_at')
        }),
    )

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url)
        return "-"

    thumbnail.short_description = 'Image'

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                               obj.image.url)
        return "No image uploaded"

    thumbnail_preview.short_description = 'Preview'

    def journeys_count(self, obj):
        """Display count of associated journeys"""
        count = obj.image_journeys.count()
        return count

    journeys_count.short_description = 'Journeys'

    def journeys_list_display(self, obj):
        """Display a formatted list of associated journeys"""
        journeys = obj.image_journeys.select_related('journey').all()
        if not journeys:
            return "No journeys associated. Use the table below to add journeys."

        html = "<div style='margin-bottom: 15px;'>"
        html += "<h4>Currently Associated Journeys:</h4>"
        html += "<table style='width:100%; border-collapse: collapse;'>"
        html += "<tr style='background: #f8f9fa;'><th>Journey</th><th>Primary</th><th>Caption</th><th>Order</th></tr>"

        for link in journeys:
            primary_star = "⭐ Yes" if link.is_primary else "No"
            html += f"<tr style='border-bottom: 1px solid #eee;'>"
            html += f"<td><strong>{link.journey.name}</strong></td>"
            html += f"<td>{primary_star}</td>"
            html += f"<td>{link.caption or '-'}</td>"
            html += f"<td>{link.order}</td>"
            html += f"</tr>"

        html += "</table>"
        html += "</div>"
        return format_html(html)

    journeys_list_display.short_description = 'Current Journey Links'

    def get_queryset(self, request):
        """Optimize queryset with prefetch_related"""
        return super().get_queryset(request).prefetch_related(
            'image_journeys__journey'
        )


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_count', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'order']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['images']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Cover Image', {
            'fields': ('cover_image',)
        }),
        ('Images', {
            'fields': ('images',),
            'description': 'Select images to include in this album'
        }),
        ('Status', {
            'fields': ('is_active', 'order', 'created_at', 'updated_at')
        }),
    )

    def image_count(self, obj):
        return obj.images.count()

    image_count.short_description = 'Images'


@admin.register(GalleryTag)
class GalleryTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(GalleryImageJourney)
class GalleryImageJourneyAdmin(admin.ModelAdmin):
    list_display = ['image_thumbnail', 'journey_name', 'is_primary', 'order']
    list_filter = ['is_primary', 'journey']
    search_fields = ['image__title', 'journey__name', 'caption']
    list_editable = ['is_primary', 'order']
    autocomplete_fields = ['image', 'journey']
    list_select_related = ['image', 'journey']

    fieldsets = (
        ('Relationship', {
            'fields': ('image', 'journey')
        }),
        ('Metadata', {
            'fields': ('is_primary', 'caption', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'image_preview']

    def image_thumbnail(self, obj):
        if obj.image and obj.image.image:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.image.image.url)
        return "-"

    image_thumbnail.short_description = 'Image'

    def image_preview(self, obj):
        if obj.image and obj.image.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                               obj.image.image.url)
        return "No image"

    image_preview.short_description = 'Image Preview'

    def journey_name(self, obj):
        return obj.journey.name

    journey_name.short_description = 'Journey'
    journey_name.admin_order_field = 'journey__name'