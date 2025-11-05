"""
URL configuration for media app.
"""

from django.urls import path
from . import views

app_name = 'media'

urlpatterns = [
    # Media
    path('', views.MediaListView.as_view(), name='media_list'),
    path('<uuid:pk>/', views.MediaDetailView.as_view(), name='media_detail'),
    path('<uuid:pk>/verify/', views.MediaVerifyView.as_view(), name='media_verify'),
]

