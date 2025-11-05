"""
Views for organizations app.
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Organization, OrganizationMembership
from .serializers import (
    OrganizationSerializer,
    OrganizationCreateSerializer,
    OrganizationMembershipSerializer,
    AddMemberSerializer,
)


class OrganizationListView(generics.ListAPIView):
    """
    List all organizations (for super admin) or user's organizations.
    """
    queryset = Organization.objects.filter(is_active=True)
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List organizations",
        description="Get list of organizations",
        tags=["Organizations"]
    )
    def get_queryset(self):
        user = self.request.user
        
        # Super admins can see all organizations
        if user.is_superuser:
            return super().get_queryset()
        
        # Regular users see only their organizations
        return Organization.objects.filter(
            memberships__user=user,
            memberships__is_active=True,
            is_active=True
        ).distinct()


class OrganizationCreateView(generics.CreateAPIView):
    """
    Create a new organization.
    Only super admins or authorized users can create organizations.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Create organization",
        description="Create a new organization",
        tags=["Organizations"]
    )
    def post(self, request, *args, **kwargs):
        # Check if user has permission to create organizations
        if not request.user.is_superuser:
            # You can add custom permission logic here
            return Response(
                {"error": "You don't have permission to create organizations"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization = serializer.save()
        
        # Add creator as admin member
        OrganizationMembership.objects.create(
            organization=organization,
            user=request.user,
            role='admin',
            invited_by=request.user
        )
        
        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_201_CREATED
        )


class OrganizationDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific organization.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get organization detail",
        description="Get details of a specific organization",
        tags=["Organizations"]
    )
    def get_queryset(self):
        user = self.request.user
        
        # Super admins can see all organizations
        if user.is_superuser:
            return super().get_queryset()
        
        # Regular users can only see organizations they belong to
        return Organization.objects.filter(
            memberships__user=user,
            memberships__is_active=True
        ).distinct()


class OrganizationUpdateView(generics.UpdateAPIView):
    """
    Update an organization.
    Only organization admins can update.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Update organization",
        description="Update organization details (admin only)",
        tags=["Organizations"]
    )
    def get_queryset(self):
        user = self.request.user
        
        # Super admins can update all organizations
        if user.is_superuser:
            return super().get_queryset()
        
        # Regular users can only update organizations where they are admin
        return Organization.objects.filter(
            memberships__user=user,
            memberships__role='admin',
            memberships__is_active=True
        ).distinct()


class OrganizationMemberListView(generics.ListAPIView):
    """
    List all members of an organization.
    """
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List organization members",
        description="Get list of all members in an organization",
        tags=["Organizations"]
    )
    def get_queryset(self):
        org_id = self.kwargs.get('org_id')
        
        # Check if user has access to this organization
        user = self.request.user
        if not user.is_superuser:
            # Verify user is a member of this organization
            if not OrganizationMembership.objects.filter(
                organization_id=org_id,
                user=user,
                is_active=True
            ).exists():
                return OrganizationMembership.objects.none()
        
        return OrganizationMembership.objects.filter(
            organization_id=org_id
        ).select_related('user', 'organization', 'invited_by')


class AddMemberView(APIView):
    """
    Add a member to an organization.
    Only organization admins can add members.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Add organization member",
        description="Add a new member to the organization (admin only)",
        tags=["Organizations"],
        request=AddMemberSerializer,
        responses={201: OrganizationMembershipSerializer}
    )
    def post(self, request, org_id):
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is an admin of this organization
        if not request.user.is_superuser:
            membership = OrganizationMembership.objects.filter(
                organization=organization,
                user=request.user,
                role='admin',
                is_active=True
            ).first()
            
            if not membership:
                return Response(
                    {"error": "You don't have permission to add members to this organization"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = AddMemberSerializer(
            data=request.data,
            context={'organization': organization}
        )
        serializer.is_valid(raise_exception=True)
        
        # Create membership
        membership = OrganizationMembership.objects.create(
            organization=organization,
            user=serializer.validated_data['user_id'],
            role=serializer.validated_data['role'],
            invited_by=request.user
        )
        
        return Response(
            OrganizationMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED
        )


class MembershipDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or remove a membership.
    """
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'membership_id'
    
    @extend_schema(
        summary="Get membership detail",
        description="Get details of a specific membership",
        tags=["Organizations"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update membership",
        description="Update membership details (admin only)",
        tags=["Organizations"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Remove membership",
        description="Remove a member from organization (admin only)",
        tags=["Organizations"]
    )
    def delete(self, request, *args, **kwargs):
        membership = self.get_object()
        membership.is_active = False
        membership.save()
        return Response(
            {"message": "Member removed from organization"},
            status=status.HTTP_200_OK
        )
    
    def get_queryset(self):
        org_id = self.kwargs.get('org_id')
        user = self.request.user
        
        # Check if user has access to this organization
        if not user.is_superuser:
            # Verify user is an admin of this organization
            if not OrganizationMembership.objects.filter(
                organization_id=org_id,
                user=user,
                role='admin',
                is_active=True
            ).exists():
                return OrganizationMembership.objects.none()
        
        return OrganizationMembership.objects.filter(
            organization_id=org_id
        ).select_related('user', 'organization', 'invited_by')

