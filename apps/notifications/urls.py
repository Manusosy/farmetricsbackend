"""
URL configuration for notifications app.
"""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notifications
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<uuid:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('mark-read/', views.NotificationMarkReadView.as_view(), name='notification_mark_read'),
    path('unread-count/', views.NotificationUnreadCountView.as_view(), name='notification_unread_count'),
    
    # Preferences
    path('preferences/', views.NotificationPreferenceView.as_view(), name='notification_preferences'),
]

