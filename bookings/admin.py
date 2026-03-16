from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'booking_date', 'guests', 'created_at']
    search_fields = ['name', 'email', 'package']
    list_filter = ['booking_date', 'created_at']
