from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('', views.MerchandiseListView.as_view(), name='merchandise-list'),
    path('<int:id>/', views.MerchandiseDetailView.as_view(), name='merchandise-detail'),
    path('category/<int:category_id>/', views.MerchandiseByCategoryView.as_view(), name='merchandise-by-category'),

    # Admin endpoints
    path('admin/create/', views.MerchandiseCreateView.as_view(), name='merchandise-create'),
    path('admin/update/<int:id>/', views.MerchandiseUpdateView.as_view(), name='merchandise-update'),
    path('admin/delete/<int:id>/', views.MerchandiseDeleteView.as_view(), name='merchandise-delete'),
]
