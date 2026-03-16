from rest_framework import serializers
from .models import Merchandise
from merchandise_category.serializers import MerchandiseCategorySerializer

class MerchandiseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_details = MerchandiseCategorySerializer(source='category', read_only=True)

    class Meta:
        model = Merchandise
        fields = [
            'id', 'name', 'category', 'category_name', 'category_details',
            'description', 'story', 'quick_facts',  # added story & quick_facts
            'price', 'stock', 'image', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    # Optional: validate quick_facts to ensure it's a list of strings
    def validate_quick_facts(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("quick_facts must be a list.")
        for item in value:
            if not isinstance(item, str):
                raise serializers.ValidationError("All quick facts must be strings.")
        return value