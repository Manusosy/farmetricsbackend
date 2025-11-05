"""
URL configuration for farms app.
"""

from django.urls import path
from . import views

app_name = 'farms'

urlpatterns = [
    # Farms
    path('', views.FarmListView.as_view(), name='farm_list'),
    path('<uuid:pk>/', views.FarmDetailView.as_view(), name='farm_detail'),
    path('<uuid:pk>/verify/', views.FarmVerifyView.as_view(), name='farm_verify'),
    path('nearby/', views.FarmNearbyView.as_view(), name='farm_nearby'),
    
    # History
    path('<uuid:farm_id>/history/', views.FarmHistoryListView.as_view(), name='farm_history'),
    
    # Boundary points
    path('<uuid:farm_id>/boundary-points/', views.FarmBoundaryPointListView.as_view(), name='farm_boundary_points'),
]

