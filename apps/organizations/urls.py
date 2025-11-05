"""
URL configuration for organizations app.
"""

from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    # Organizations
    path('', views.OrganizationListView.as_view(), name='organization_list'),
    path('<uuid:pk>/', views.OrganizationDetailView.as_view(), name='organization_detail'),
    path('create/', views.OrganizationCreateView.as_view(), name='organization_create'),
    path('<uuid:pk>/update/', views.OrganizationUpdateView.as_view(), name='organization_update'),
    
    # Memberships
    path('<uuid:org_id>/members/', views.OrganizationMemberListView.as_view(), name='member_list'),
    path('<uuid:org_id>/members/add/', views.AddMemberView.as_view(), name='add_member'),
    path('<uuid:org_id>/members/<uuid:membership_id>/', views.MembershipDetailView.as_view(), name='membership_detail'),
]

