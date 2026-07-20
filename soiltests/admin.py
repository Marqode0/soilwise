from django.contrib import admin
from .models import SoilSample, TestResult

@admin.register(SoilSample)
class SoilSampleAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'farm', 'status', 'collection_date', 'created_at']
    list_filter = ['status']
    search_fields = ['barcode', 'farm__name']
    
    fieldsets = (
        (None, {
            'fields': ('farm', 'barcode', 'status')
        }),
        ('Optional Information', {
            'fields': ('agent', 'collection_date', 'lab_received_date', 'notes'),
            'classes': ('collapse',),
        }),
    )

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['sample', 'nitrogen_ppm', 'phosphorus_ppm', 'potassium_ppm', 'ph_level']
    list_filter = ['tested_at']
    
    fieldsets = (
        (None, {
            'fields': ('sample', 'nitrogen_ppm', 'phosphorus_ppm', 'potassium_ppm', 'ph_level')
        }),
        ('Optional Information', {
            'fields': ('organic_matter_percent', 'recommendations', 'tested_by'),
            'classes': ('collapse',),
        }),
    )