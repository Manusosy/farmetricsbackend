"""
URL configuration for regions app.
"""

from django.urls import path
from . import views

app_name = 'regions'

urlpatterns = [
    # Regions
    path('', views.RegionListView.as_view(), name='region_list'),
    path('<uuid:pk>/', views.RegionDetailView.as_view(), name='region_detail'),
    path('hierarchy/', views.RegionHierarchyView.as_view(), name='region_hierarchy'),
    path('<uuid:pk>/children/', views.RegionChildrenView.as_view(), name='region_children'),
    
    # Supervisors
    path('<uuid:region_id>/supervisors/', views.RegionSupervisorListView.as_view(), name='region_supervisors'),
]

