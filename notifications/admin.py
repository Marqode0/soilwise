from django.contrib import admin
from .models import NotificationLog

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'channel', 'subject', 'sent_at', 'is_delivered']
    list_filter = ['channel', 'is_delivered']
    search_fields = ['user__username', 'subject']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'channel', 'subject', 'message')
        }),
        ('Delivery Status', {
            'fields': ('is_delivered', 'delivery_response'),
            'classes': ('collapse',),
        }),
    )