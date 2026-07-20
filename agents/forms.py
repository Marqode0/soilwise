from django import forms
from .models import AgentApplication, LabTechApplication

class AgentApplicationForm(forms.ModelForm):
    class Meta:
        model = AgentApplication
        fields = ['display_name', 'gender', 'full_name', 'phone_number', 'location', 'experience', 'education', 'reason', 'nin']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Summer, Agent007'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '080XXXXXXXX'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, State, Nigeria'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your farming or agricultural experience...'}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'List your relevant education and qualifications...'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Why do you want to become an agent?'}),
            'nin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678901', 'maxlength': '11'}),
        }
        labels = {
            'display_name': 'Agent Display Name',
            'gender': 'Gender',
            'full_name': 'Full Name',
            'phone_number': 'Phone Number',
            'location': 'Location',
            'experience': 'Farming/Agri Experience',
            'education': 'Education & Qualifications',
            'reason': 'Why do you want to be an agent?',
            'nin': 'NIN (National Identification Number)',
        }

class LabTechApplicationForm(forms.ModelForm):
    class Meta:
        model = LabTechApplication
        fields = ['full_name', 'phone_number', 'location', 'qualifications', 'experience', 'reason', 'nin']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '080XXXXXXXX'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, State, Nigeria'}),
            'qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List your relevant qualifications and certifications...'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your lab experience...'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Why do you want to become a lab technician?'}),
            'nin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678901', 'maxlength': '11'}),
        }
        labels = {
            'full_name': 'Full Name',
            'phone_number': 'Phone Number',
            'location': 'Location',
            'qualifications': 'Qualifications & Certifications',
            'experience': 'Lab Experience',
            'reason': 'Why do you want to be a lab technician?',
            'nin': 'NIN (National Identification Number)',
        }