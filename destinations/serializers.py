from rest_framework import serializers
from .models import Destination

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'slug', 'icon', 'short_description', 'description',
            'tags', 'featured_image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class DestinationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views
    """
    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'slug', 'icon', 'short_description',
            'featured_image', 'tags'
        ]


class DestinationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single destination view
    """
    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'slug', 'icon', 'short_description', 'description',
            'tags', 'featured_image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']