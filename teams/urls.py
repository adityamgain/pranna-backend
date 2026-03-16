from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('members/', views.TeamMemberListCreateView.as_view(), name='member-list-create'),
    path('members/<slug:slug>/', views.TeamMemberRetrieveUpdateDeleteView.as_view(), name='member-detail'),
    path('members/search/', views.TeamMemberSearchView.as_view(), name='member-search'),
    path('members/stats/', views.TeamMemberStatsView.as_view(), name='member-stats'),
]