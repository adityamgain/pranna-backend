from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('', views.MerchandiseCategoryListView.as_view(), name='category-list'),
    path('<int:id>/', views.MerchandiseCategoryDetailView.as_view(), name='category-detail'),

    # Admin endpoints
    path('admin/create/', views.MerchandiseCategoryCreateView.as_view(), name='category-create'),
    path('admin/update/<int:id>/', views.MerchandiseCategoryUpdateView.as_view(), name='category-update'),
    path('admin/delete/<int:id>/', views.MerchandiseCategoryDeleteView.as_view(), name='category-delete'),
]