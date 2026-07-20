from django import forms
from .models import SoilSample
from farms.models import Farm
from accounts.models import User

class SoilTestRequestForm(forms.ModelForm):
    agent = forms.ModelChoiceField(
        queryset=User.objects.filter(role='agent', is_approved=True),
        empty_label="Select an Agent",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Choose Your Agent"
    )
    
    collection_location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., No. 5, Farm Road, Kaduna',
            'id': 'collection_location'
        }),
        label="Collection Location"
    )
    
    gps_coordinates = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 10.5236, 7.4375',
            'id': 'gps_coordinates'
        }),
        label="GPS Coordinates (optional)"
    )
    
    class Meta:
        model = SoilSample
        fields = ['farm', 'agent', 'collection_location', 'gps_coordinates', 'notes']
        widgets = {
            'farm': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any specific concerns about your soil?'}),
        }
        labels = {
            'farm': 'Select Farm',
            'agent': 'Choose Your Agent',
            'notes': 'Additional Notes (optional)',
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['farm'].queryset = Farm.objects.filter(farmer=user)
        self.fields['agent'].queryset = User.objects.filter(
            role='agent',
            is_approved=True
        )