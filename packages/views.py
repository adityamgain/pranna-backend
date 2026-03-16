from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Package
from .serializers import PackageSerializer

# ---------- Public Endpoints ----------

class PackageListView(generics.ListAPIView):
    """
    GET: List all packages (public)
    Supports optional filtering by query parameters (e.g., ?is_featured=true)
    """
    queryset = Package.objects.all().order_by('-is_featured', 'name')
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]
    # You can add DjangoFilterBackend here if needed, but basic filtering is not required


@api_view(['GET'])
@permission_classes([AllowAny])
def package_search(request):
    """
    GET: Search packages by name, short_description, or description.
    Query param: ?q=searchterm
    """
    query = request.query_params.get('q', '')
    if query:
        packages = Package.objects.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query)
        ).distinct().order_by('-is_featured', 'name')
    else:
        packages = Package.objects.none()
    serializer = PackageSerializer(packages, many=True)
    return Response(serializer.data)


class PackageDetailView(generics.RetrieveAPIView):
    """
    GET: Retrieve a package by its slug.
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


# ---------- Admin Endpoints ----------

class PackageCreateView(generics.CreateAPIView):
    """
    POST: Create a new package (admin only).
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAdminUser]


class PackageUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH: Update a package by slug (admin only).
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'


class PackageDeleteView(generics.DestroyAPIView):
    """
    DELETE: Delete a package by slug (admin only).
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'slug'


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_all_packages(request):
    """
    DELETE: Remove all packages (use with caution, admin only).
    """
    count = Package.objects.count()
    Package.objects.all().delete()
    return Response(
        {'message': f'Successfully deleted {count} packages.'},
        status=status.HTTP_204_NO_CONTENT
    )