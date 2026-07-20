from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('agent', 'Collection Agent'),
        ('lab_tech', 'Lab Technician'),
        ('admin', 'Administrator'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='farmer')
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    
    # For agents and lab techs
    agent_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    lab_tech_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    
    # Approval status
    is_approved = models.BooleanField(default=False)  # False = pending
    rejection_message = models.TextField(blank=True, null=True)
    
    # For farmers - which agent they are assigned to
    assigned_agent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_farmers', limit_choices_to={'role': 'agent'})
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"