def notifications(request):

    if not request.user.is_authenticated:
        return {
            'notifications': [],
            'unread_notifications_count': 0,
        }

    user_notifications = request.user.notifications.all()

    return {
        'notifications': user_notifications[:10],
        'unread_notifications_count': user_notifications.filter(
            is_read=False
        ).count(),
    }