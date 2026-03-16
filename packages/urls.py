from django.urls import path
from . import views

app_name = 'packages'  # optional

urlpatterns = [
    # Public endpoints
    path('', views.PackageListView.as_view(), name='package-list'),
    path('search/', views.package_search, name='package-search'),
    path('<slug:slug>/', views.PackageDetailView.as_view(), name='package-detail'),

    # Admin endpoints
    path('admin/create/', views.PackageCreateView.as_view(), name='package-create'),
    path('admin/update/<slug:slug>/', views.PackageUpdateView.as_view(), name='package-update'),
    path('admin/delete/<slug:slug>/', views.PackageDeleteView.as_view(), name='package-delete'),
    path('admin/delete-all/', views.delete_all_packages, name='package-delete-all'),
]