"""
Serializers for accounts app.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from datetime import timedelta
from .models import User, Role, UserRole, PasswordResetToken


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    primary_organization = serializers.SerializerMethodField()
    primary_role = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'employee_id', 'avatar', 'address', 
            'city', 'state', 'country', 'is_active', 'email_verified',
            'phone_verified', 'mfa_enabled', 'primary_organization',
            'primary_role', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'last_login', 'email_verified', 'phone_verified']
    
    def get_primary_organization(self, obj):
        org = obj.primary_organization
        if org:
            return {'id': str(org.id), 'name': org.name, 'slug': org.slug}
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 
            'last_name', 'phone_number', 'employee_id'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
        else:
            raise serializers.ValidationError('Must include "email" and "password".')
        
        attrs['user'] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField(required=True)
    
    def save(self):
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
            # Create password reset token
            token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            # TODO: Send email with reset link
            return token
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            pass
        return None


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_token(self, value):
        try:
            token = PasswordResetToken.objects.get(token=value)
            if not token.is_valid:
                raise serializers.ValidationError('Token is invalid or has expired.')
            return token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError('Invalid token.')
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs
    
    def save(self):
        token = self.validated_data['token']
        user = token.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        token.mark_as_used()
        return user


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'organization', 'organization_name', 'name', 'slug',
            'description', 'permissions', 'is_system_role', 'is_active',
            'user_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        return obj.user_assignments.filter(is_active=True).count()


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    is_expired_status = serializers.BooleanField(source='is_expired', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_email', 'user_name', 'role', 'role_name',
            'assigned_by', 'assigned_by_name', 'assigned_at', 'is_active',
            'expires_at', 'is_expired_status', 'created_at'
        ]
        read_only_fields = ['id', 'assigned_at', 'created_at']

