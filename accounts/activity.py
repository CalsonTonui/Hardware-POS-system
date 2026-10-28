from .models import ActivityLog


def log_activity(
    request,
    action,
    description,
    target_type=None,
    target_id=None,
):
    """
    Helper function to log a user action.

    Args:
        request: The HTTP request object (needs .user, .META)
        action: Action code from ActivityLog.ACTION_CHOICES
        description: Human-readable description
        target_type: Optional - 'Product', 'Sale', 'User', etc.
        target_id: Optional - ID of the affected object
    """
    user = request.user if request.user.is_authenticated else None

    # Extract IP address
    ip_address = (
        request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        or request.META.get('REMOTE_ADDR')
    )

    # Extract user agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:300]

    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            description=description,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address or None,
            user_agent=user_agent or None,
        )
    except Exception:
        # Never let logging break the app
        pass