"""
Utility functions for sending notifications.
"""

from .models import Notification, NotificationPreference
from django.contrib.auth import get_user_model

User = get_user_model()


def create_notification(
    user,
    notification_type,
    title,
    message,
    priority='normal',
    action_url='',
    action_text='',
    related_farmer=None,
    related_farm=None,
    related_visit=None,
    related_request=None,
    metadata=None
):
    """
    Create a notification for a user.
    
    Args:
        user: User instance to notify
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        priority: Priority level (default: 'normal')
        action_url: URL to navigate to
        action_text: Text for action button
        related_*: Related objects
        metadata: Additional metadata dict
    
    Returns:
        Notification instance
    """
    # Check user preferences
    try:
        prefs = user.notification_preferences
        if not prefs.preferences.get(notification_type, True):
            # User has disabled this notification type
            return None
    except NotificationPreference.DoesNotExist:
        # No preferences set, allow all notifications
        pass
    
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        action_url=action_url,
        action_text=action_text,
        related_farmer=related_farmer,
        related_farm=related_farm,
        related_visit=related_visit,
        related_request=related_request,
        metadata=metadata or {}
    )
    
    # TODO: Send via WebSocket if connected
    # TODO: Send email if enabled
    # TODO: Send push notification if enabled
    
    return notification


def notify_visit_submitted(visit):
    """Create notification when visit is submitted."""
    # Notify supervisor/assigned reviewer
    # This is a placeholder - implement based on your assignment logic
    pass


def notify_visit_approved(visit):
    """Create notification when visit is approved."""
    create_notification(
        user=visit.field_officer,
        notification_type='visit_approved',
        title=f"Visit {visit.visit_code} Approved",
        message=f"Your visit to {visit.farm.name} has been approved.",
        action_url=f"/visits/{visit.id}/",
        action_text="View Visit",
        related_visit=visit
    )


def notify_visit_rejected(visit):
    """Create notification when visit is rejected."""
    create_notification(
        user=visit.field_officer,
        notification_type='visit_rejected',
        title=f"Visit {visit.visit_code} Rejected",
        message=f"Your visit to {visit.farm.name} has been rejected. Reason: {visit.rejection_reason}",
        action_url=f"/visits/{visit.id}/",
        action_text="View Visit",
        related_visit=visit
    )


def notify_request_created(request):
    """Create notification when request is created."""
    if request.assigned_to:
        create_notification(
            user=request.assigned_to,
            notification_type='request_created',
            title=f"New {request.get_request_type_display()}",
            message=f"{request.requested_by.get_full_name()} created a new request: {request.title}",
            action_url=f"/requests/{request.id}/",
            action_text="Review Request",
            related_request=request
        )


def notify_request_approved(request):
    """Create notification when request is approved."""
    create_notification(
        user=request.requested_by,
        notification_type='request_approved',
        title=f"Request {request.request_code} Approved",
        message=f"Your request '{request.title}' has been approved.",
        action_url=f"/requests/{request.id}/",
        action_text="View Request",
        related_request=request
    )


def notify_request_rejected(request):
    """Create notification when request is rejected."""
    create_notification(
        user=request.requested_by,
        notification_type='request_rejected',
        title=f"Request {request.request_code} Rejected",
        message=f"Your request '{request.title}' has been rejected. Reason: {request.rejection_reason}",
        action_url=f"/requests/{request.id}/",
        action_text="View Request",
        related_request=request
    )

