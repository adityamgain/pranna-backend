from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.contact_submit, name='contact-submit'),
    path('messages/', views.ContactListCreateView.as_view(), name='contact-list'),
    path('messages/<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
]
