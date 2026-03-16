from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count
from .models import Testimonial
from .serializers import TestimonialSerializer

class TestimonialListCreateView(generics.ListCreateAPIView):
    """
    GET: List all testimonials (ordered by newest first)
    POST: Create a new testimonial (admin only if needed)
    """
    queryset = Testimonial.objects.all().order_by('-created_at')
    serializer_class = TestimonialSerializer
    # Uncomment the next line if you want to restrict creation to admins
    # permission_classes = [permissions.IsAdminUser]


class TestimonialRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a testimonial by primary key (id)
    PUT/PATCH: Update a testimonial (admin only if needed)
    DELETE: Delete a testimonial (admin only if needed)
    """
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    lookup_field = 'pk'  # Use primary key (id)
    # permission_classes = [permissions.IsAdminUser]


class TestimonialSearchView(generics.ListAPIView):
    """
    GET: Search testimonials by author_name or content.
    Example: /testimonials/search/?q=John
    """
    serializer_class = TestimonialSerializer

    def get_queryset(self):
        queryset = Testimonial.objects.all().order_by('-created_at')
        query = self.request.query_params.get('q', '')
        if query:
            queryset = queryset.filter(
                models.Q(author_name__icontains=query) |
                models.Q(content__icontains=query)
            )
        return queryset


class TestimonialStatsView(APIView):
    """
    GET: Return statistics about testimonials.
    """
    def get(self, request, format=None):
        total = Testimonial.objects.count()
        featured = Testimonial.objects.filter(is_featured=True).count()
        avg_rating = Testimonial.objects.aggregate(Avg('rating'))['rating__avg']
        rating_distribution = Testimonial.objects.values('rating').annotate(count=Count('rating')).order_by('rating')

        data = {
            'total': total,
            'featured': featured,
            'average_rating': round(avg_rating, 2) if avg_rating else None,
            'rating_distribution': list(rating_distribution),
        }
        return Response(data, status=status.HTTP_200_OK)