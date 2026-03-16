from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import MerchandiseCategory
from .serializers import MerchandiseCategorySerializer

class MerchandiseCategoryListView(generics.ListAPIView):
    """
    API endpoint for listing merchandise categories
    """
    queryset = MerchandiseCategory.objects.filter(is_active=True)
    serializer_class = MerchandiseCategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

class MerchandiseCategoryDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific merchandise category
    """
    queryset = MerchandiseCategory.objects.filter(is_active=True)
    serializer_class = MerchandiseCategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

# Admin endpoints
class MerchandiseCategoryCreateView(generics.CreateAPIView):
    """
    API endpoint for creating a merchandise category (admin only)
    """
    queryset = MerchandiseCategory.objects.all()
    serializer_class = MerchandiseCategorySerializer
    permission_classes = [permissions.IsAdminUser]

class MerchandiseCategoryUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating a merchandise category (admin only)
    """
    queryset = MerchandiseCategory.objects.all()
    serializer_class = MerchandiseCategorySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'

class MerchandiseCategoryDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting a merchandise category (admin only)
    """
    queryset = MerchandiseCategory.objects.all()
    serializer_class = MerchandiseCategorySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'