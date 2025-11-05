"""
Views for accounts app (authentication and user management).
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Role, UserRole
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    RoleSerializer,
    UserRoleSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    Create a new user account.
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register new user",
        description="Create a new user account with email and password",
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    User login endpoint.
    Authenticate user and return JWT tokens.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    
    @extend_schema(
        summary="Login user",
        description="Authenticate user with email and password, returns JWT tokens",
        tags=["Authentication"],
        request=LoginSerializer,
        responses={200: UserSerializer}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Update last login IP
        user.last_login_ip = self.get_client_ip(request)
        user.save(update_fields=['last_login_ip'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        })
    
    def get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    """
    User logout endpoint.
    Blacklist the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Logout user",
        description="Blacklist the refresh token to logout user",
        tags=["Authentication"]
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """
    Change user password (requires authentication).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change password for authenticated user",
        tags=["Authentication"],
        request=PasswordChangeSerializer
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    Request password reset.
    Sends password reset email with token.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Request password reset",
        description="Send password reset email to user",
        tags=["Authentication"],
        request=PasswordResetRequestSerializer
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'If the email exists, a password reset link has been sent'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Confirm password reset",
        description="Reset password using reset token",
        tags=["Authentication"],
        request=PasswordResetConfirmSerializer
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password reset successful'
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveAPIView):
    """
    Get current user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get user profile",
        description="Get authenticated user's profile",
        tags=["Profile"]
    )
    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """
    Update current user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Update user profile",
        description="Update authenticated user's profile",
        tags=["Profile"]
    )
    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    List all users (admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    @extend_schema(
        summary="List users",
        description="Get list of all users (admin only)",
        tags=["Users"]
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization if provided
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(
                organization_memberships__organization=self.request.organization,
                organization_memberships__is_active=True
            ).distinct()
        
        # Filter by search query
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
        
        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a specific user (admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    @extend_schema(
        summary="Get user detail",
        description="Get details of a specific user (admin only)",
        tags=["Users"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user",
        description="Update a specific user (admin only)",
        tags=["Users"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete user",
        description="Delete a specific user (admin only)",
        tags=["Users"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class RoleListCreateView(generics.ListCreateAPIView):
    """
    List all roles or create a new role.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List roles",
        description="Get list of all roles",
        tags=["Roles"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create role",
        description="Create a new role (admin only)",
        tags=["Roles"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by organization if provided
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        # Only show active roles by default
        if self.request.query_params.get('include_inactive') != 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a specific role.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get role detail",
        description="Get details of a specific role",
        tags=["Roles"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update role",
        description="Update a specific role (admin only)",
        tags=["Roles"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete role",
        description="Delete a specific role (admin only)",
        tags=["Roles"]
    )
    def delete(self, request, *args, **kwargs):
        # Prevent deletion of system roles
        role = self.get_object()
        if role.is_system_role:
            return Response(
                {"error": "System roles cannot be deleted"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().delete(request, *args, **kwargs)

