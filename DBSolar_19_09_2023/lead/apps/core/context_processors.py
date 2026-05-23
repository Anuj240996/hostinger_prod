from .models import Notification

def site_settings(request):
    """Add site-wide settings to template context"""
    return {
        'site_name': 'Solar CRM',
        'company_name': 'Solar Solutions',
    }

def notifications(request):
    """Add user notifications to template context"""
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            user=request.user
        )[:5]
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return {
            'notifications': notifications,
            'unread_notifications_count': unread_count,
        }
    return {}