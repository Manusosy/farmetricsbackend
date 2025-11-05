"""
URL configuration for farmers app.
"""

from django.urls import path
from . import views

app_name = 'farmers'

urlpatterns = [
    # Farmers
    path('', views.FarmerListView.as_view(), name='farmer_list'),
    path('<uuid:pk>/', views.FarmerDetailView.as_view(), name='farmer_detail'),
    path('<uuid:pk>/verify/', views.FarmerVerifyView.as_view(), name='farmer_verify'),
    
    # Duplicate management
    path('duplicates/check/', views.FarmerDuplicateCheckView.as_view(), name='farmer_duplicate_check'),
    path('merge/', views.FarmerMergeView.as_view(), name='farmer_merge'),
    path('merge-history/', views.FarmerMergeHistoryListView.as_view(), name='farmer_merge_history'),
]

