from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Destination
from .serializers import DestinationSerializer, DestinationListSerializer, DestinationDetailSerializer

class DestinationListView(generics.ListAPIView):
    """
    API endpoint for listing all destinations
    Supports filtering by tags and search
    """
    serializer_class = DestinationListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = []
    search_fields = ['name', 'short_description', 'description', 'tags']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        queryset = Destination.objects.all()
        
        # Filter by tag if provided
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__contains=[tag])
        
        # Filter by multiple tags (comma-separated)
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            for t in tag_list:
                queryset = queryset.filter(tags__contains=[t.strip()])
        
        return queryset


class DestinationDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific destination by slug
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def destination_search(request):
    """
    Advanced search endpoint for destinations
    """
    query = request.query_params.get('q', '')
    
    if not query:
        return Response([])
    
    destinations = Destination.objects.filter(
        Q(name__icontains=query) |
        Q(short_description__icontains=query) |
        Q(description__icontains=query) |
        Q(tags__icontains=query)
    )[:20]
    
    serializer = DestinationListSerializer(destinations, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_all_tags(request):
    """
    Get all unique tags from all destinations
    """
    destinations = Destination.objects.all()
    all_tags = set()
    
    for dest in destinations:
        if dest.tags:
            all_tags.update(dest.tags)
    
    return Response(sorted(list(all_tags)))


# Admin endpoints
class DestinationCreateView(generics.CreateAPIView):
    """
    API endpoint for creating a destination (admin only)
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [permissions.IsAdminUser]


class DestinationUpdateView(generics.UpdateAPIView):
    """
    API endpoint for updating a destination (admin only)
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'


class DestinationDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting a destination (admin only)
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'


@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_all_destinations(request):
    """
    API endpoint for deleting all destinations (admin only - careful!)
    """
    count = Destination.objects.count()
    Destination.objects.all().delete()
    
    return Response({
        'success': True,
        'message': f'Successfully deleted {count} destinations'
    }, status=status.HTTP_200_OK)
