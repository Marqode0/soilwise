from django.db import models
from farms.models import Farm
from accounts.models import User

class SoilSample(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Collection'),
        ('collected', 'Collected'),
        ('in_transit', 'In Transit to Lab'),
        ('at_lab', 'At Laboratory'),
        ('testing', 'Testing in Progress'),
        ('results_ready', 'Results Ready'),
        ('completed', 'Completed'),
    )
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='samples')
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_samples')
    assigned_lab_tech = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_lab_samples',  # Unique related_name
        limit_choices_to={'role': 'lab_tech'}
    )
    barcode = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Location fields
    collection_location = models.CharField(max_length=255, blank=True, null=True, help_text="Where the sample should be collected")
    gps_coordinates = models.CharField(max_length=100, blank=True, null=True, help_text="GPS coordinates of collection point")
    
    collection_date = models.DateTimeField(null=True, blank=True)
    lab_received_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Sample {self.barcode} - {self.farm.name}"

class TestResult(models.Model):
    sample = models.OneToOneField(SoilSample, on_delete=models.CASCADE, related_name='result')
    nitrogen_ppm = models.FloatField()
    phosphorus_ppm = models.FloatField()
    potassium_ppm = models.FloatField()
    ph_level = models.FloatField()
    organic_matter_percent = models.FloatField(null=True, blank=True)
    recommendations = models.JSONField(default=dict)
    tested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tested_results')
    tested_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Result for {self.sample.barcode}"