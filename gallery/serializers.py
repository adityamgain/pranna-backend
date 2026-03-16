from rest_framework import serializers
from .models import (
    GalleryCategory, GalleryImage, GalleryAlbum,
    GalleryTag, GalleryImageJourney
)
from journey.models import Journey
from journey.serializers import JourneySerializer


class GalleryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'featured_image', 'is_active', 'order']


class JourneyBasicSerializer(serializers.ModelSerializer):
    """Basic Journey serializer for nested display"""

    class Meta:
        model = Journey
        fields = ['id', 'name', 'slug', 'icon', 'short_description', 'is_featured']


class GalleryImageJourneySerializer(serializers.ModelSerializer):
    """Serializer for the through model"""
    journey_details = JourneyBasicSerializer(source='journey', read_only=True)

    class Meta:
        model = GalleryImageJourney
        fields = ['id', 'journey', 'journey_details', 'is_primary', 'caption', 'order']


class GalleryImageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    high_res_url = serializers.SerializerMethodField()

    # Add journey metadata
    journey_details = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = [
            'id', 'title', 'slug', 'description', 'caption', 'alt_text',
            'image', 'image_url', 'high_res_image', 'high_res_url',
            'category', 'category_name', 'location', 'date_taken', 'photographer',
            'journey_details',  # Add this
            'is_featured', 'is_active', 'order', 'created_at', 'updated_at'
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_high_res_url(self, obj):
        if obj.high_res_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.high_res_image.url)
            return obj.high_res_image.url
        return None

    def get_journey_details(self, obj):
        """Return journey metadata for this image"""
        # Get all journey links for this image
        journey_links = obj.image_journeys.select_related('journey').all()

        return [
            {
                'journey_id': link.journey.id,
                'journey_name': link.journey.name,
                'journey_slug': link.journey.slug,
                'is_primary': link.is_primary,
                'caption': link.caption,
                'order': link.order
            }
            for link in journey_links
        ]


class GalleryAlbumSerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, read_only=True)
    image_count = serializers.SerializerMethodField()

    class Meta:
        model = GalleryAlbum
        fields = [
            'id', 'name', 'slug', 'description', 'cover_image',
            'images', 'image_count', 'is_active', 'order',
            'created_at', 'updated_at'
        ]

    def get_image_count(self, obj):
        return obj.images.filter(is_active=True).count()


class GalleryTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryTag
        fields = ['id', 'name', 'slug']