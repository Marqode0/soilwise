from django import forms
from .models import Farm

class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['name', 'location', 'size_hectares', 'primary_crop', 'gps_coordinates']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter farm name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Kaduna, Nigeria'}),
            'size_hectares': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2.5'}),
            'primary_crop': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Maize'}),
            'gps_coordinates': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 10.5236, 7.4375'}),
        }
        labels = {
            'gps_coordinates': 'GPS Coordinates (optional)',
        }