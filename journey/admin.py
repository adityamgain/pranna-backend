from django.contrib import admin
from django import forms
from .models import Journey
import json


class JourneyAdminForm(forms.ModelForm):
    class Meta:
        model = Journey
        fields = '__all__'
        widgets = {
            'quick_facts': forms.Textarea(attrs={
                'rows': 5,
                'class': 'vLargeTextField',
                'placeholder': '["Fact 1", "Fact 2", "Fact 3"]'
            }),
            'includes': forms.Textarea(attrs={
                'rows': 5,
                'class': 'vLargeTextField',
                'placeholder': '["Item 1", "Item 2", "Item 3"]'
            }),
            'excludes': forms.Textarea(attrs={
                'rows': 5,
                'class': 'vLargeTextField',
                'placeholder': '["Item 1", "Item 2", "Item 3"]'
            }),
        }

    def clean_quick_facts(self):
        data = self.cleaned_data['quick_facts']
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format. Use: ['Fact 1', 'Fact 2']")
        return data

    def clean_includes(self):
        data = self.cleaned_data['includes']
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format. Use: ['Item 1', 'Item 2']")
        return data

    def clean_excludes(self):
        data = self.cleaned_data['excludes']
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format. Use: ['Item 1', 'Item 2']")
        return data


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    form = JourneyAdminForm

    list_display = ['name', 'level', 'is_featured', 'created_at', 'quick_facts_count', 'includes_count']
    list_filter = ['level', 'is_featured']
    search_fields = ['name', 'short_description', 'description']
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'icon', 'is_featured')
        }),
        ('Descriptions', {
            'fields': ('short_description', 'description')
        }),
        ('Journey Details', {
            'fields': ('level',)
        }),
        ('Quick Facts', {
            'fields': ('quick_facts',),
            'description': 'Enter as JSON array: ["Fact 1", "Fact 2", "Fact 3"]'
        }),
        ('Included/Not Included', {
            'fields': ('includes', 'excludes'),
            'description': 'Enter as JSON arrays: ["Item 1", "Item 2", "Item 3"]'
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def quick_facts_count(self, obj):
        if obj.quick_facts:
            return len(obj.quick_facts)
        return 0

    quick_facts_count.short_description = 'Quick Facts'

    def includes_count(self, obj):
        if obj.includes:
            return len(obj.includes)
        return 0

    includes_count.short_description = 'Included Items'