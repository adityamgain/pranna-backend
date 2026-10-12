from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    # Public endpoints
    path('', views.EventListView.as_view(), name='event-list'),
    path('upcoming/', views.UpcomingEventListView.as_view(), name='event-upcoming'),
    path('calendar/', views.event_calendar, name='event-calendar'),
    path('calendar.ics', views.event_calendar_feed, name='event-calendar-feed'),

    # Admin endpoints
    path('admin/', views.EventAdminListView.as_view(), name='event-admin-list'),
    path('admin/create/', views.EventCreateView.as_view(), name='event-create'),
    path('admin/update/<slug:slug>/', views.EventUpdateView.as_view(), name='event-update'),
    path('admin/delete/<slug:slug>/', views.EventDeleteView.as_view(), name='event-delete'),

    path('<slug:slug>/', views.EventDetailView.as_view(), name='event-detail'),
    path('<slug:slug>/ics/', views.event_ics, name='event-ics'),
]
