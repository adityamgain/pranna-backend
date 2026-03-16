
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Merchandise
from .serializers import MerchandiseSerializer
from merchandise_category.models import MerchandiseCategory

class MerchandiseListView(generics.ListAPIView):
    """
    API endpoint for listing merchandise items
    """
    queryset = Merchandise.objects.filter(is_active=True)
    serializer_class = MerchandiseSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']

class MerchandiseDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific merchandise item
    """
    queryset = Merchandise.objects.filter(is_active=True)
    serializer_class = MerchandiseSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

class MerchandiseByCategoryView(generics.ListAPIView):
    """
    API endpoint for listing merchandise items by category
    """
    serializer_class = MerchandiseSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Merchandise.objects.filter(category_id=category_id, is_active=True)

# Admin endpoints
class MerchandiseCreateView(generics.CreateAPIView):
    """
    API endpoint for creating a merchandise item (admin only)
    """
    queryset = Merchandise.objects.all()
    serializer_class = MerchandiseSerializer
    permission_classes = [permissions.IsAdminUser]

class MerchandiseUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating a merchandise item (admin only)
    """
    queryset = Merchandise.objects.all()
    serializer_class = MerchandiseSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'

class MerchandiseDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting a merchandise item (admin only)
    """
    queryset = Merchandise.objects.all()
    serializer_class = MerchandiseSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'
