from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('', views.GalleryListView.as_view(), name='gallery-list'),
    path('featured/', views.GalleryFeaturedView.as_view(), name='gallery-featured'),
    path('<int:id>/', views.GalleryDetailView.as_view(), name='gallery-detail'),
    path('category/<int:category_id>/', views.GalleryByCategoryView.as_view(), name='gallery-by-category'),
    path('category/<slug:category_slug>/', views.GalleryByCategorySlugView.as_view(), name='gallery-by-category-slug'),
    path('album/<int:album_id>/', views.GalleryByAlbumView.as_view(), name='gallery-by-album'),
    path('location/<str:location>/', views.GalleryByLocationView.as_view(), name='gallery-by-location'),

    # Admin endpoints
    path('admin/categories/', views.GalleryCategoryListView.as_view(), name='gallery-category-list'),
    path('admin/categories/create/', views.GalleryCategoryCreateView.as_view(), name='gallery-category-create'),
    path('admin/categories/update/<int:id>/', views.GalleryCategoryUpdateView.as_view(),
         name='gallery-category-update'),
    path('admin/categories/delete/<int:id>/', views.GalleryCategoryDeleteView.as_view(),
         name='gallery-category-delete'),

    path('admin/images/create/', views.GalleryImageCreateView.as_view(), name='gallery-image-create'),
    path('admin/images/update/<int:id>/', views.GalleryImageUpdateView.as_view(), name='gallery-image-update'),
    path('admin/images/delete/<int:id>/', views.GalleryImageDeleteView.as_view(), name='gallery-image-delete'),

    path('admin/albums/create/', views.GalleryAlbumCreateView.as_view(), name='gallery-album-create'),
    path('admin/albums/update/<int:id>/', views.GalleryAlbumUpdateView.as_view(), name='gallery-album-update'),
    path('admin/albums/delete/<int:id>/', views.GalleryAlbumDeleteView.as_view(), name='gallery-album-delete'),
]