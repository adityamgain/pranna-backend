from rest_framework import serializers
from .models import Newsletter_Mails


class NewsletterMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter_Mails
        fields = ['id', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_email(self, value):
        """Check if email already exists"""
        if Newsletter_Mails.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already subscribed.")
        return value

