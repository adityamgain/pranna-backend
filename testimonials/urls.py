from django.urls import path
from . import views

app_name = 'testimonials'

urlpatterns = [
    path('', views.TestimonialListCreateView.as_view(), name='testimonial-list-create'),
    path('<int:pk>/', views.TestimonialRetrieveUpdateDeleteView.as_view(), name='testimonial-detail'),
    path('search/', views.TestimonialSearchView.as_view(), name='testimonial-search'),
    path('stats/', views.TestimonialStatsView.as_view(), name='testimonial-stats'),
]