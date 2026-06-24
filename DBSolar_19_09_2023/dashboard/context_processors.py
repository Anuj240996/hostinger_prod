"""Template context shared across ERP and Lead CRM nav bars."""


def staff_nav_notifications(request):
    """Unread staff notifications (same data as /index/ nav bell)."""
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'count1': 0, 'notification1': []}

    from dashboard.models import staff_Notification

    notification1 = staff_Notification.objects.filter(
        staff_id=request.user.id,
        status=0,
    ).select_related('sender', 'sender__profile').order_by('-created_at')

    return {
        'count1': notification1.count(),
        'notification1': notification1,
    }
