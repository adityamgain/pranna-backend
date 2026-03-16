from django.contrib import admin
from .models import Newsletter_Mails
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
import csv
from datetime import datetime


@admin.register(Newsletter_Mails)
class NewsletterMailsAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at', 'actions_column']
    list_filter = ['created_at']
    search_fields = ['email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    actions = ['export_as_csv', 'delete_selected']

    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'created_at')
        }),
    )

    def actions_column(self, obj):
        return format_html(
            '<a class="button" href="{}" onclick="return confirm(\'Are you sure?\');">Delete</a>',
            reverse('admin:newsletter_newsletter_mails_delete', args=[obj.pk])
        )

    actions_column.short_description = 'Actions'
    actions_column.allow_tags = True

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = f'attachment; filename=newsletter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export selected as CSV"

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_delete_permission(self, request, obj=None):
        return True

    # Customize admin templates
    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }

