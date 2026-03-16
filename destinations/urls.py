from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('', views.DestinationListView.as_view(), name='destination-list'),
    path('search/', views.destination_search, name='destination-search'),
    path('tags/', views.get_all_tags, name='destination-tags'),
    path('<slug:slug>/', views.DestinationDetailView.as_view(), name='destination-detail'),

    # Admin endpoints
    path('admin/create/', views.DestinationCreateView.as_view(), name='destination-create'),
    path('admin/update/<slug:slug>/', views.DestinationUpdateView.as_view(), name='destination-update'),
    path('admin/delete/<slug:slug>/', views.DestinationDeleteView.as_view(), name='destination-delete'),
    path('admin/delete-all/', views.delete_all_destinations, name='destination-delete-all'),
]