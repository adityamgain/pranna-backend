from rest_framework import serializers
from .models import Journey


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = [
            'id', 'name', 'slug', 'icon', 'short_description', 'description',
            'level', 'quick_facts', 'includes', 'excludes', 'featured_image',
            'is_featured', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']