from django.db import models
from accounts.models import User

class NotificationLog(models.Model):
    CHANNEL_CHOICES = (
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_logs')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)
    delivery_response = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.channel} - {self.sent_at}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"