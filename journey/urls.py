from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('', views.JourneyListView.as_view(), name='journey-list'),
    path('featured/', views.JourneyFeaturedView.as_view(), name='journey-featured'),
    path('<slug:slug>/', views.JourneyDetailView.as_view(), name='journey-detail'),

    # Admin endpoints
    path('admin/create/', views.JourneyCreateView.as_view(), name='journey-create'),
    path('admin/update/<slug:slug>/', views.JourneyUpdateView.as_view(), name='journey-update'),
    path('admin/delete/<slug:slug>/', views.JourneyDeleteView.as_view(), name='journey-delete'),
]