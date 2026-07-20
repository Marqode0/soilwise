from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'is_approved', 'agent_id', 'lab_tech_id', 'assigned_agent')
    list_filter = ('role', 'is_approved')
    search_fields = ('username', 'email', 'phone_number', 'agent_id', 'lab_tech_id')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('phone_number', 'role', 'is_approved', 'rejection_message', 'agent_id', 'lab_tech_id', 'assigned_agent'),
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('phone_number', 'role', 'is_approved', 'agent_id', 'lab_tech_id'),
        }),
    )
    
    actions = ['approve_users', 'reject_users']
    
    def approve_users(self, request, queryset):
        queryset.update(is_approved=True, rejection_message=None)
        self.message_user(request, 'Users approved successfully.')
    approve_users.short_description = "Approve selected users"
    
    def reject_users(self, request, queryset):
        for user in queryset:
            user.is_approved = False
            user.save()
        self.message_user(request, 'Users rejected.')
    reject_users.short_description = "Reject selected users"

admin.site.register(User, CustomUserAdmin)