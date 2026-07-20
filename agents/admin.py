from django.contrib import admin
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import AgentProfile, Kit, AgentApplication, LabTechApplication, LabTechContract, WithdrawalRequest
from notifications.models import Notification

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'gender', 'tier', 'total_collections', 'total_commission_earned']
    list_filter = ['tier', 'gender']
    search_fields = ['user__username', 'display_name']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'display_name', 'gender', 'tier')
        }),
        ('Stats', {
            'fields': ('total_collections', 'total_commission_earned', 'kits_assigned', 'kits_used'),
            'classes': ('collapse',),
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'bank_account_number', 'bank_account_name'),
            'classes': ('collapse',),
        }),
    )

@admin.register(Kit)
class KitAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'assigned_to', 'is_used']
    list_filter = ['is_used']
    search_fields = ['serial_number']
    
    fieldsets = (
        (None, {
            'fields': ('serial_number', 'assigned_to', 'is_used')
        }),
        ('Optional Information', {
            'fields': ('used_on_sample',),
            'classes': ('collapse',),
        }),
    )

@admin.register(AgentApplication)
class AgentApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'gender', 'nin', 'status', 'applied_at']
    list_filter = ['status', 'gender']
    search_fields = ['user__username', 'display_name', 'phone_number', 'nin']
    actions = ['approve_agent_application', 'reject_agent_application']
    
    def approve_agent_application(self, request, queryset):
        for application in queryset:
            if application.status == 'pending':
                user = application.user
                user.role = 'agent'
                user.is_approved = True
                user.save()
                
                agent_id = f"AGENT{str(user.id).zfill(5)}"
                AgentProfile.objects.create(
                    user=user,
                    display_name=application.display_name,
                    gender=application.gender,
                    tier='bronze'
                )
                
                application.status = 'approved'
                application.reviewed_at = timezone.now()
                application.save()
                
                Notification.objects.create(
                    user=user,
                    title='🎉 Agent Application Approved!',
                    message=f'''Congratulations! Your application to become a SoilWise Agent has been APPROVED.

Your Agent Display Name: {application.display_name}
Your Agent ID: {agent_id}

You can now:
✅ Login as an agent
✅ Accept soil collection requests
✅ Earn ₦200 per sample collected'''
                )
                
                try:
                    send_mail(
                        subject='🎉 Agent Application Approved – SoilWise',
                        message=f'''Hello {application.user.username},

Congratulations! Your application to become a SoilWise Agent has been APPROVED.

Your Agent Display Name: {application.display_name}
Your Agent ID: {agent_id}

Login here: http://127.0.0.1:8000/accounts/login/

- The SoilWise Team''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[application.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    pass
                    
        self.message_user(request, 'Agent applications approved.')
    approve_agent_application.short_description = "Approve Agent Applications"
    
    def reject_agent_application(self, request, queryset):
        for application in queryset:
            if application.status == 'pending':
                application.status = 'rejected'
                application.reviewed_at = timezone.now()
                application.save()
                
                Notification.objects.create(
                    user=application.user,
                    title='❌ Agent Application Rejected',
                    message=f'Your agent application was rejected.\n\nReason: {application.rejection_message or "We are unable to approve your application at this time."}'
                )
                
                try:
                    send_mail(
                        subject='Agent Application – SoilWise',
                        message=f'''Hello {application.user.username},

Thank you for your interest in becoming a SoilWise Agent.

Unfortunately, your application has been rejected for the following reason:

{application.rejection_message or "We are unable to approve your application at this time."}

- The SoilWise Team''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[application.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    pass
                    
        self.message_user(request, 'Agent applications rejected.')
    reject_agent_application.short_description = "Reject Agent Applications"
    
    fieldsets = (
        (None, {
            'fields': ('user', 'display_name', 'gender', 'full_name', 'phone_number', 'location', 'nin')
        }),
        ('Application Details', {
            'fields': ('experience', 'education', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'rejection_message', 'applied_at', 'reviewed_at')
        }),
    )
    readonly_fields = ['applied_at', 'reviewed_at']

@admin.register(LabTechApplication)
class LabTechApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'nin', 'status', 'applied_at']
    list_filter = ['status']
    search_fields = ['user__username', 'full_name', 'phone_number', 'nin']
    actions = ['approve_labtech_application', 'reject_labtech_application']
    
    def approve_labtech_application(self, request, queryset):
        for application in queryset:
            if application.status == 'pending':
                user = application.user
                user.role = 'lab_tech'
                user.is_approved = True
                user.save()
                
                application.status = 'approved'
                application.reviewed_at = timezone.now()
                application.save()
                
                Notification.objects.create(
                    user=user,
                    title='🎉 Lab Tech Application Approved!',
                    message=f'''Congratulations! Your application to become a SoilWise Lab Technician has been APPROVED.

Please sign your employment contract to complete the process.

Click here to sign your contract: http://127.0.0.1:8000/agents/contract/'''
                )
                
                try:
                    send_mail(
                        subject='🎉 Lab Tech Application Approved – SoilWise',
                        message=f'''Hello {application.user.username},

Congratulations! Your application to become a SoilWise Lab Technician has been APPROVED.

Please sign your employment contract to complete the process:

http://127.0.0.1:8000/agents/contract/

- The SoilWise Team''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[application.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    pass
                    
        self.message_user(request, 'Lab Tech applications approved. Users redirected to contract signing.')
    approve_labtech_application.short_description = "Approve Lab Tech Applications"
    
    def reject_labtech_application(self, request, queryset):
        for application in queryset:
            if application.status == 'pending':
                application.status = 'rejected'
                application.reviewed_at = timezone.now()
                application.save()
                
                Notification.objects.create(
                    user=application.user,
                    title='❌ Lab Tech Application Rejected',
                    message=f'Your lab technician application was rejected.\n\nReason: {application.rejection_message or "We are unable to approve your application at this time."}'
                )
                
                try:
                    send_mail(
                        subject='Lab Tech Application – SoilWise',
                        message=f'''Hello {application.user.username},

Thank you for your interest in becoming a SoilWise Lab Technician.

Unfortunately, your application has been rejected for the following reason:

{application.rejection_message or "We are unable to approve your application at this time."}

- The SoilWise Team''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[application.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    pass
                    
        self.message_user(request, 'Lab Tech applications rejected.')
    reject_labtech_application.short_description = "Reject Lab Tech Applications"
    
    fieldsets = (
        (None, {
            'fields': ('user', 'full_name', 'phone_number', 'location', 'nin')
        }),
        ('Application Details', {
            'fields': ('qualifications', 'experience', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'rejection_message', 'applied_at', 'reviewed_at')
        }),
    )
    readonly_fields = ['applied_at', 'reviewed_at']

@admin.register(LabTechContract)
class LabTechContractAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'signed_at', 'approved_at']
    list_filter = ['status']
    search_fields = ['user__username']
    actions = ['approve_contracts', 'reject_contracts']
    
    def approve_contracts(self, request, queryset):
        for contract in queryset:
            if contract.status == 'pending':
                contract.status = 'approved'
                contract.approved_at = timezone.now()
                contract.save()
                
                Notification.objects.create(
                    user=contract.user,
                    title='✅ Contract Approved!',
                    message=f'Your lab technician contract has been approved. You can now start working!'
                )
                
                try:
                    send_mail(
                        subject='Contract Approved – SoilWise',
                        message=f'''Hello {contract.user.username},

Your lab technician contract has been APPROVED.

You can now start working as a lab technician.

Login here: http://127.0.0.1:8000/accounts/login/

- The SoilWise Team''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[contract.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    pass
                    
        self.message_user(request, 'Contracts approved.')
    approve_contracts.short_description = "Approve selected contracts"
    
    def reject_contracts(self, request, queryset):
        for contract in queryset:
            if contract.status == 'pending':
                contract.status = 'rejected'
                contract.save()
                
                Notification.objects.create(
                    user=contract.user,
                    title='❌ Contract Rejected',
                    message=f'Your lab technician contract was rejected. Please contact admin for more information.'
                )
                
                try:
                    send_mail(
                        subject='Contract Rejected – SoilWise',
                        message=f'''Hello {contract.user.username},

Your lab technician contract has been REJECTED.

Please contact admin for more information.

- The SoilWise Team''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[contract.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    pass
                    
        self.message_user(request, 'Contracts rejected.')
    reject_contracts.short_description = "Reject selected contracts"
    
    fieldsets = (
        (None, {
            'fields': ('user', 'status')
        }),
        ('Contract Details', {
            'fields': ('contract_text', 'signed_at', 'approved_at')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',)
        }),
    )
    readonly_fields = ['signed_at', 'approved_at', 'contract_text']

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['agent', 'amount', 'bank_name', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['agent__username', 'bank_account_number']
    actions = ['approve_withdrawal', 'complete_withdrawal', 'reject_withdrawal']
    
    def approve_withdrawal(self, request, queryset):
        for withdrawal in queryset:
            if withdrawal.status == 'pending':
                withdrawal.status = 'approved'
                withdrawal.processed_at = timezone.now()
                withdrawal.save()
                
                Notification.objects.create(
                    user=withdrawal.agent,
                    title='✅ Withdrawal Approved',
                    message=f'Your withdrawal request of ₦{withdrawal.amount} has been approved. It will be processed shortly.'
                )
        self.message_user(request, 'Withdrawals approved.')
    approve_withdrawal.short_description = "Approve selected withdrawals"
    
    def complete_withdrawal(self, request, queryset):
        for withdrawal in queryset:
            if withdrawal.status == 'approved':
                withdrawal.status = 'completed'
                withdrawal.processed_at = timezone.now()
                withdrawal.save()
                
                Notification.objects.create(
                    user=withdrawal.agent,
                    title='💰 Withdrawal Completed',
                    message=f'Your withdrawal of ₦{withdrawal.amount} has been completed.'
                )
        self.message_user(request, 'Withdrawals marked as completed.')
    complete_withdrawal.short_description = "Mark as completed"
    
    def reject_withdrawal(self, request, queryset):
        for withdrawal in queryset:
            if withdrawal.status == 'pending':
                withdrawal.status = 'rejected'
                withdrawal.save()
                
                # Refund the money
                profile = AgentProfile.objects.get(user=withdrawal.agent)
                profile.total_earnings += withdrawal.amount
                profile.pending_earnings -= withdrawal.amount
                profile.save()
                
                Notification.objects.create(
                    user=withdrawal.agent,
                    title='❌ Withdrawal Rejected',
                    message=f'Your withdrawal request of ₦{withdrawal.amount} was rejected. The amount has been refunded to your wallet.'
                )
        self.message_user(request, 'Withdrawals rejected and refunded.')
    reject_withdrawal.short_description = "Reject selected withdrawals"