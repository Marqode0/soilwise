from django.db import models
from accounts.models import User

class Farm(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    size_hectares = models.FloatField()
    primary_crop = models.CharField(max_length=100)
    gps_coordinates = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.farmer.username}"