from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_location', 'rating', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'rating']
    search_fields = ['author_name', 'content']
    list_editable = ['is_featured']
    readonly_fields = ['created_at']