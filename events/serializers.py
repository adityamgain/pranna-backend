from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    destination_name = serializers.CharField(source='destination.name', read_only=True, default=None)
    journey_name = serializers.CharField(source='journey.name', read_only=True, default=None)
    journey_slug = serializers.CharField(source='journey.slug', read_only=True, default=None)
    package_name = serializers.CharField(source='package.name', read_only=True, default=None)
    package_slug = serializers.CharField(source='package.slug', read_only=True, default=None)
    is_sold_out = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'event_type', 'event_type_display', 'icon',
            'short_description', 'description',
            'start', 'end', 'all_day',
            'location', 'destination', 'destination_name',
            'journey', 'journey_name', 'journey_slug',
            'package', 'package_name', 'package_slug',
            'price', 'price_display', 'capacity', 'spots_left', 'is_sold_out', 'registration_url',
            'featured_image', 'color_hex', 'is_featured', 'is_published',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def validate(self, attrs):
        start = attrs.get('start', getattr(self.instance, 'start', None))
        end = attrs.get('end', getattr(self.instance, 'end', None))
        if start and end and end < start:
            raise serializers.ValidationError({'end': 'End must be after start.'})
        capacity = attrs.get('capacity', getattr(self.instance, 'capacity', None))
        spots_left = attrs.get('spots_left', getattr(self.instance, 'spots_left', None))
        if capacity is not None and spots_left is not None and spots_left > capacity:
            raise serializers.ValidationError({'spots_left': 'Spots left cannot exceed capacity.'})
        return attrs


class CalendarEventSerializer(serializers.ModelSerializer):
    """Compact representation for calendar grids."""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    is_sold_out = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'event_type', 'event_type_display', 'icon',
            'start', 'end', 'all_day', 'location', 'color_hex',
            'is_featured', 'is_sold_out', 'spots_left',
        ]
