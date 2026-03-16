from rest_framework import serializers
from .models import MerchandiseCategory

class MerchandiseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchandiseCategory
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
