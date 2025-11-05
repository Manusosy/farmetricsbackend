"""
URL configuration for requests app.
"""

from django.urls import path
from . import views

app_name = 'requests'

urlpatterns = [
    # Requests
    path('', views.RequestListView.as_view(), name='request_list'),
    path('<uuid:pk>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('<uuid:pk>/approve/', views.RequestApproveView.as_view(), name='request_approve'),
    
    # Transfer requests
    path('transfer/', views.TransferRequestCreateView.as_view(), name='transfer_request_create'),
    
    # Comments
    path('<uuid:request_id>/comments/', views.RequestCommentListView.as_view(), name='request_comments'),
]

