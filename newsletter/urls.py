from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('subscribe/api/', views.newsletter_subscribe_api, name='newsletter-subscribe-api'),
    path('unsubscribe/<str:email>/', views.NewsletterUnsubscribeView.as_view(), name='newsletter-unsubscribe'),

    # Admin endpoints
    path('admin/list/', views.NewsletterMailListView.as_view(), name='newsletter-list'),
    path('admin/<int:pk>/', views.NewsletterMailDetailView.as_view(), name='newsletter-detail'),
    path('admin/delete/<int:pk>/', views.NewsletterMailDeleteView.as_view(), name='newsletter-delete'),
    path('admin/delete-all/', views.newsletter_delete_all, name='newsletter-delete-all'),
]