from rest_framework import serializers
from .models import TeamMember


class TeamMemberListSerializer(serializers.ModelSerializer):
    """Serializer for list view (lightweight)"""

    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'position', 'slug', 'short_description', 'image', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class TeamMemberDetailSerializer(serializers.ModelSerializer):
    """Serializer for detail view (full data)"""

    class Meta:
        model = TeamMember
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class TeamMemberCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create/update operations"""

    class Meta:
        model = TeamMember
        fields = ['name', 'position', 'linkedin', 'email', 'instagram',
                  'short_description', 'image']

    def validate_email(self, value):
        """Optional: Add custom email validation"""
        if value and TeamMember.objects.filter(email=value).exists():
            raise serializers.ValidationError("A team member with this email already exists.")
        return value