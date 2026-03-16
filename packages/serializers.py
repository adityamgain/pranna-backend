from rest_framework import serializers
from .models import Package
from destinations.models import Destination          # <-- add this
from journey.models import Journey                  # <-- add this
from destinations.serializers import DestinationSerializer
from journey.serializers import JourneySerializer

class PackageSerializer(serializers.ModelSerializer):
    # Nested read-only representations
    locations_detail = DestinationSerializer(source='locations', many=True, read_only=True)
    services_detail = JourneySerializer(source='services', many=True, read_only=True)

    # For convenience, include primary key lists for writing
    location_ids = serializers.PrimaryKeyRelatedField(
        source='locations', queryset=Destination.objects.all(), many=True, write_only=True
    )
    service_ids = serializers.PrimaryKeyRelatedField(
        source='services', queryset=Journey.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Package
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'slug']