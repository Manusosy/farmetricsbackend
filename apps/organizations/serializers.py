"""
Serializers for organizations app.
"""

from rest_framework import serializers
from .models import Organization, OrganizationMembership
from apps.accounts.serializers import UserSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""
    
    member_count = serializers.IntegerField(read_only=True)
    is_enterprise_tier = serializers.BooleanField(source='is_enterprise', read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description', 'email', 'phone_number',
            'address', 'subscription_tier', 'settings', 'is_active',
            'logo', 'member_count', 'is_enterprise_tier', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an organization."""
    
    class Meta:
        model = Organization
        fields = [
            'name', 'description', 'email', 'phone_number', 'address',
            'subscription_tier', 'logo'
        ]


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationMembership model."""
    
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True, required=False)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.get_full_name', read_only=True)
    
    class Meta:
        model = OrganizationMembership
        fields = [
            'id', 'organization', 'organization_name', 'user', 'user_id',
            'role', 'is_active', 'invited_by', 'invited_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'invited_by']


class AddMemberSerializer(serializers.Serializer):
    """Serializer for adding a member to an organization."""
    
    user_id = serializers.UUIDField(required=True)
    role = serializers.ChoiceField(
        choices=OrganizationMembership.ROLE_CHOICES,
        default='field_officer'
    )
    
    def validate_user_id(self, value):
        from apps.accounts.models import User
        try:
            user = User.objects.get(id=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
    
    def validate(self, attrs):
        # Check if user is already a member
        organization = self.context.get('organization')
        user = attrs['user_id']
        
        if OrganizationMembership.objects.filter(
            organization=organization,
            user=user
        ).exists():
            raise serializers.ValidationError("User is already a member of this organization")
        
        return attrs

