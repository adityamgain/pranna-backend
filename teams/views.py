from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .models import TeamMember
from .serializers import (
    TeamMemberListSerializer,
    TeamMemberDetailSerializer,
    TeamMemberCreateUpdateSerializer
)


# Custom pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data
        })


# List all team members or create new one
class TeamMemberListCreateView(generics.ListCreateAPIView):
    queryset = TeamMember.objects.all().order_by('-created_at')  # Add ordering
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TeamMemberCreateUpdateSerializer
        return TeamMemberListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Team member created successfully',
            'data': TeamMemberDetailSerializer(serializer.instance).data
        }, status=status.HTTP_201_CREATED)


# Retrieve, update or delete a specific team member
class TeamMemberRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeamMember.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TeamMemberCreateUpdateSerializer
        return TeamMemberDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'status': 'success',
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'message': 'Team member updated successfully',
            'data': TeamMemberDetailSerializer(serializer.instance).data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': 'success',
            'message': 'Team member deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


# Search team members
class TeamMemberSearchView(generics.ListAPIView):
    serializer_class = TeamMemberListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = TeamMember.objects.all()
        search_term = self.request.query_params.get('q', None)

        if search_term:
            queryset = queryset.filter(
                models.Q(name__icontains=search_term) |
                models.Q(position__icontains=search_term) |
                models.Q(short_description__icontains=search_term)
            )
        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })


# Stats view
class TeamMemberStatsView(APIView):
    def get(self, request):
        total_members = TeamMember.objects.count()
        members_with_linkedin = TeamMember.objects.exclude(linkedin__isnull=True).exclude(linkedin__exact='').count()
        members_with_instagram = TeamMember.objects.exclude(instagram__isnull=True).exclude(instagram__exact='').count()

        return Response({
            'status': 'success',
            'data': {
                'total_members': total_members,
                'members_with_linkedin': members_with_linkedin,
                'members_with_instagram': members_with_instagram,
            }
        })