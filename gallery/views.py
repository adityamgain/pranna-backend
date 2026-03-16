from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .models import GalleryCategory, GalleryImage, GalleryAlbum
from .serializers import (
    GalleryCategorySerializer, GalleryImageSerializer,
    GalleryAlbumSerializer
)


# ==================== PUBLIC VIEWS ====================

class GalleryListView(generics.ListAPIView):
    """
    List all active gallery images with optional filtering
    GET /api/gallery/
    """
    serializer_class = GalleryImageSerializer
    permission_classes = []  # Public access

    def get_queryset(self):
        queryset = GalleryImage.objects.filter(is_active=True)

        # Filter by category
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Filter by featured
        featured = self.request.query_params.get('featured', None)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)

        # Filter by location
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)

        # ADD THIS - Filter by journey
        journey_id = self.request.query_params.get('journey', None)
        if journey_id:
            queryset = queryset.filter(image_journeys__journey_id=journey_id)

        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(caption__icontains=search) |
                Q(location__icontains=search)
            )

        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        return queryset.order_by(ordering)


class GalleryFeaturedView(generics.ListAPIView):
    """
    List featured gallery images
    GET /api/gallery/featured/
    """
    serializer_class = GalleryImageSerializer
    permission_classes = []  # Public access

    def get_queryset(self):
        limit = self.request.query_params.get('limit', 8)
        try:
            limit = int(limit)
        except ValueError:
            limit = 8

        return GalleryImage.objects.filter(
            is_active=True,
            is_featured=True
        ).order_by('?')[:limit]  # Random order


class GalleryDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific gallery image by ID
    GET /api/gallery/<id>/
    """
    serializer_class = GalleryImageSerializer
    permission_classes = []  # Public access
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        return GalleryImage.objects.filter(is_active=True)


class GalleryByCategoryView(generics.ListAPIView):
    """
    List all images in a specific category by category ID
    GET /api/gallery/category/<category_id>/
    """
    serializer_class = GalleryImageSerializer
    permission_classes = []  # Public access

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(
            GalleryCategory.objects.filter(is_active=True),
            id=category_id
        )

        return GalleryImage.objects.filter(
            is_active=True,
            category=category
        ).order_by('order', '-created_at')


class GalleryByCategorySlugView(generics.ListAPIView):
    """
    List all images in a specific category by category slug
    GET /api/gallery/category/<category_slug>/
    """
    serializer_class = GalleryImageSerializer
    permission_classes = []  # Public access

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(
            GalleryCategory.objects.filter(is_active=True),
            slug=category_slug
        )

        return GalleryImage.objects.filter(
            is_active=True,
            category=category
        ).order_by('order', '-created_at')


class GalleryByAlbumView(generics.ListAPIView):
    """
    List all images in a specific album by album ID
    GET /api/gallery/album/<album_id>/
    """
    serializer_class = GalleryImageSerializer
    permission_classes = []  # Public access

    def get_queryset(self):
        album_id = self.kwargs.get('album_id')
        album = get_object_or_404(
            GalleryAlbum.objects.filter(is_active=True),
            id=album_id
        )

        return album.images.filter(is_active=True).order_by('order', '-created_at')


class GalleryByLocationView(generics.ListAPIView):
    """
    List all images from a specific location
    GET /api/gallery/location/<location>/
    """
    serializer_class = GalleryImageSerializer
    permission_classes = []  # Public access

    def get_queryset(self):
        location = self.kwargs.get('location')
        return GalleryImage.objects.filter(
            is_active=True,
            location__icontains=location
        ).order_by('-created_at')


# ==================== ADMIN CATEGORY VIEWS ====================

class GalleryCategoryListView(generics.ListAPIView):
    """
    List all gallery categories (admin)
    GET /api/gallery/admin/categories/
    """
    serializer_class = GalleryCategorySerializer
    permission_classes = [IsAdminUser]
    queryset = GalleryCategory.objects.all().order_by('order', 'name')


class GalleryCategoryCreateView(generics.CreateAPIView):
    """
    Create a new gallery category (admin)
    POST /api/gallery/admin/categories/create/
    """
    serializer_class = GalleryCategorySerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()


class GalleryCategoryUpdateView(generics.UpdateAPIView):
    """
    Update a gallery category by ID (admin)
    PUT/PATCH /api/gallery/admin/categories/update/<id>/
    """
    serializer_class = GalleryCategorySerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = GalleryCategory.objects.all()


class GalleryCategoryDeleteView(generics.DestroyAPIView):
    """
    Delete a gallery category by ID (admin)
    DELETE /api/gallery/admin/categories/delete/<id>/
    """
    serializer_class = GalleryCategorySerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = GalleryCategory.objects.all()


# ==================== ADMIN IMAGE VIEWS ====================

class GalleryImageCreateView(generics.CreateAPIView):
    """
    Create a new gallery image (admin)
    POST /api/gallery/admin/images/create/
    """
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()


class GalleryImageUpdateView(generics.UpdateAPIView):
    """
    Update a gallery image by ID (admin)
    PUT/PATCH /api/gallery/admin/images/update/<id>/
    """
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = GalleryImage.objects.all()


class GalleryImageDeleteView(generics.DestroyAPIView):
    """
    Delete a gallery image by ID (admin)
    DELETE /api/gallery/admin/images/delete/<id>/
    """
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = GalleryImage.objects.all()


# ==================== ADMIN ALBUM VIEWS ====================

class GalleryAlbumCreateView(generics.CreateAPIView):
    """
    Create a new gallery album (admin)
    POST /api/gallery/admin/albums/create/
    """
    serializer_class = GalleryAlbumSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()


class GalleryAlbumUpdateView(generics.UpdateAPIView):
    """
    Update a gallery album by ID (admin)
    PUT/PATCH /api/gallery/admin/albums/update/<id>/
    """
    serializer_class = GalleryAlbumSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = GalleryAlbum.objects.all()


class GalleryAlbumDeleteView(generics.DestroyAPIView):
    """
    Delete a gallery album by ID (admin)
    DELETE /api/gallery/admin/albums/delete/<id>/
    """
    serializer_class = GalleryAlbumSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = GalleryAlbum.objects.all()