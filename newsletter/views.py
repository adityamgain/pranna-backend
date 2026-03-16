from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from .models import Newsletter_Mails
from .serializers import NewsletterMailSerializer


class NewsletterSubscribeView(generics.CreateAPIView):
    """
    API endpoint for subscribing to newsletter
    """
    queryset = Newsletter_Mails.objects.all()
    serializer_class = NewsletterMailSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Send welcome email (optional)
        try:
            email = serializer.validated_data['email']
            send_mail(
                'Welcome to Pranna Wellness Newsletter',
                'Thank you for subscribing to our newsletter. You will receive updates about new journeys, products, and teachings.',
                settings.DEFAULT_FROM_EMAIL or 'noreply@pranna.com',
                [email],
                fail_silently=True,
            )
        except:
            pass  # Email sending failed, but subscription still successful

        return Response({
            'success': True,
            'message': 'Successfully subscribed to newsletter',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class NewsletterUnsubscribeView(generics.DestroyAPIView):
    """
    API endpoint for unsubscribing from newsletter
    """
    queryset = Newsletter_Mails.objects.all()
    serializer_class = NewsletterMailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'email'
    lookup_url_kwarg = 'email'

    def get_object(self):
        email = self.kwargs.get('email')
        try:
            return Newsletter_Mails.objects.get(email=email)
        except Newsletter_Mails.DoesNotExist:
            return None

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            self.perform_destroy(instance)
            return Response({
                'success': True,
                'message': 'Successfully unsubscribed from newsletter'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Email not found in newsletter list'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def newsletter_subscribe_api(request):
    """
    Alternative simple endpoint for newsletter subscription
    """
    email = request.data.get('email')

    if not email:
        return Response({
            'success': False,
            'message': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if email already exists
    if Newsletter_Mails.objects.filter(email=email).exists():
        return Response({
            'success': False,
            'message': 'This email is already subscribed'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create new subscription
    subscription = Newsletter_Mails.objects.create(email=email)

    return Response({
        'success': True,
        'message': 'Successfully subscribed to newsletter',
        'data': {
            'id': subscription.id,
            'email': subscription.email,
            'created_at': subscription.created_at
        }
    }, status=status.HTTP_201_CREATED)


# Admin endpoints
class NewsletterMailListView(generics.ListAPIView):
    """
    API endpoint for listing all newsletter subscribers (admin only)
    """
    queryset = Newsletter_Mails.objects.all()
    serializer_class = NewsletterMailSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['email']
    search_fields = ['email']


class NewsletterMailDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting a subscriber (admin only)
    """
    queryset = Newsletter_Mails.objects.all()
    serializer_class = NewsletterMailSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'


class NewsletterMailDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific subscriber (admin only)
    """
    queryset = Newsletter_Mails.objects.all()
    serializer_class = NewsletterMailSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'


@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def newsletter_delete_all(request):
    """
    API endpoint for deleting all subscribers (admin only - careful!)
    """
    count = Newsletter_Mails.objects.count()
    Newsletter_Mails.objects.all().delete()

    return Response({
        'success': True,
        'message': f'Successfully deleted {count} subscribers'
    }, status=status.HTTP_200_OK)

