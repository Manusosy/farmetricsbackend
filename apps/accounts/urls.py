"""
URL configuration for accounts app (authentication endpoints).
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password management
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    
    # Users management (admin)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Roles
    path('roles/', views.RoleListCreateView.as_view(), name='role_list_create'),
    path('roles/<uuid:pk>/', views.RoleDetailView.as_view(), name='role_detail'),
]

