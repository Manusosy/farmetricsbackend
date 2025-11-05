"""
URL configuration for visits app.
"""

from django.urls import path
from . import views

app_name = 'visits'

urlpatterns = [
    # Visits
    path('', views.VisitListView.as_view(), name='visit_list'),
    path('<uuid:pk>/', views.VisitDetailView.as_view(), name='visit_detail'),
    path('<uuid:pk>/submit/', views.VisitSubmitView.as_view(), name='visit_submit'),
    path('<uuid:pk>/approve/', views.VisitApproveView.as_view(), name='visit_approve'),
    
    # Comments
    path('<uuid:visit_id>/comments/', views.VisitCommentListView.as_view(), name='visit_comments'),
    
    # Media
    path('<uuid:visit_id>/media/', views.VisitMediaListView.as_view(), name='visit_media'),
]

