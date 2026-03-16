from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/contact/', include('contact.urls')),
    path('api/merchandise/', include('merchandise.urls')),
    path('api/merchandise-categories/', include('merchandise_category.urls')),
    path('api/journeys/', include('journey.urls')),
    path('api/newsletter/', include('newsletter.urls')),
    path('api/destinations/', include('destinations.urls')),
    path('api/packages/', include('packages.urls')),
    path('api/checkout/', include('checkout.urls')),
    path('api/teams/', include('teams.urls')),
    path('api/gallery/', include('gallery.urls')),
    path('api/testimonials/', include('testimonials.urls')),

    # path('jet/', include('jet.urls', 'jet')),  # JET UI components
    # path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)