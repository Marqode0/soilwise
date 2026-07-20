from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import NotificationLog

@login_required
def notification_history(request):
    notifications = NotificationLog.objects.filter(user=request.user).order_by('-sent_at')
    return render(request, 'notifications/history.html', {'notifications': notifications})