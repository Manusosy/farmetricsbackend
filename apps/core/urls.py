"""
URL configuration for core app (audit logs, search, analytics).
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Audit Logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_log_list'),
    path('audit-logs/<uuid:pk>/', views.AuditLogDetailView.as_view(), name='audit_log_detail'),
    
    # Search
    path('search/', views.GlobalSearchView.as_view(), name='global_search'),
    
    # Analytics
    path('analytics/dashboard/', views.DashboardStatsView.as_view(), name='dashboard_stats'),
    path('analytics/visits/', views.VisitAnalyticsView.as_view(), name='visit_analytics'),
    path('analytics/farmers/', views.FarmerAnalyticsView.as_view(), name='farmer_analytics'),
    path('analytics/farms/', views.FarmAnalyticsView.as_view(), name='farm_analytics'),
]

