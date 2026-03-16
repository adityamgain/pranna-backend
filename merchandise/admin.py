from django.contrib import admin
from .models import Merchandise

@admin.register(Merchandise)
class MerchandiseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description', 'story']  # added 'story' to search
    list_editable = ['price', 'stock', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description', 'story')  # added 'story'
        }),
        ('Quick Facts', {
            'fields': ('quick_facts',),
            'description': 'Provide a list of quick facts as a JSON array (e.g., ["Fact 1", "Fact 2"])'
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )