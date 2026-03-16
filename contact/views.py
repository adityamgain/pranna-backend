from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Contact
from .serializers import ContactSerializer


class ContactListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating contact messages
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save()


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating or deleting a specific contact message
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def contact_submit(request):
    """
    Simple endpoint for contact form submission
    """
    serializer = ContactSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Thank you for contacting us! We will get back to you soon.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    # Return detailed error messages
    return Response({
        'success': False,
        'message': 'Please check the form for errors.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# Simple test view
from django.http import JsonResponse


def test_view(request):
    return JsonResponse({"message": "Contact app is working!", "status": "ok"})