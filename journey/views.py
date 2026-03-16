from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Journey
from .serializers import JourneySerializer


class JourneyListView(generics.ListAPIView):
    """
    API endpoint for listing journeys
    """
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured', 'level']
    search_fields = ['name', 'short_description', 'description']
    ordering_fields = ['name', 'created_at']


class JourneyDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific journey
    """
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class JourneyFeaturedView(generics.ListAPIView):
    """
    API endpoint for featured journeys
    """
    serializer_class = JourneySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Journey.objects.filter(is_featured=True)


# Admin endpoints
class JourneyCreateView(generics.CreateAPIView):
    """
    API endpoint for creating a journey (admin only)
    """
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    permission_classes = [permissions.IsAdminUser]


class JourneyUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating a journey (admin only)
    """
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'


class JourneyDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting a journey (admin only)
    """
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'