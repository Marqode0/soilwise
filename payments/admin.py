from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'payment_method', 'paid_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['user__username', 'reference']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'amount', 'reference', 'status', 'payment_method')
        }),
        ('Optional Information', {
            'fields': ('sample', 'paid_at'),
            'classes': ('collapse',),
        }),
    )