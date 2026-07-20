from django.db import models
from accounts.models import User
from soiltests.models import SoilSample

class AgentProfile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    
    TIER_CHOICES = (
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    display_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name shown on agent dashboard")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze')
    total_collections = models.IntegerField(default=0)
    total_commission_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    kits_assigned = models.IntegerField(default=0)
    kits_used = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    # Bank details for commission payments
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_account_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Earnings tracking
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pending_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.username} - {self.tier}"

class Kit(models.Model):
    serial_number = models.CharField(max_length=50, unique=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_kits')
    is_used = models.BooleanField(default=False)
    used_on_sample = models.ForeignKey(SoilSample, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Kit {self.serial_number} - {'Used' if self.is_used else 'Available'}"

class AgentApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_application')
    display_name = models.CharField(max_length=100, help_text="Name you want to appear on your agent profile")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, help_text="Select your gender")
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    experience = models.TextField(help_text="Describe your farming/agriculture experience")
    education = models.TextField(help_text="List your relevant education and qualifications")
    reason = models.TextField(help_text="Why do you want to become an agent?")
    nin = models.CharField(max_length=11, help_text="National Identification Number (11 digits)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_message = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.status}"

# ===== LAB TECH APPLICATION =====
class LabTechApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='labtech_application')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    qualifications = models.TextField(help_text="List your relevant qualifications and certifications")
    experience = models.TextField(help_text="Describe your lab experience")
    reason = models.TextField(help_text="Why do you want to become a lab technician?")
    nin = models.CharField(max_length=11, help_text="National Identification Number (11 digits)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_message = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.status}"

class LabTechContract(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='labtech_contract')
    contract_text = models.TextField()
    signed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.status}"

class CollectionRecord(models.Model):
    sample = models.OneToOneField(SoilSample, on_delete=models.CASCADE, related_name='collection_record')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    collected_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, help_text="Where the sample was collected")
    gps_coordinates = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True)
    signature = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.sample.barcode} - {self.agent.username} - {self.collected_at}"

class WithdrawalRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bank_name = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=20)
    bank_account_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.agent.username} - ₦{self.amount} - {self.status}"