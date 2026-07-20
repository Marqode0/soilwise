from django.contrib import admin
from .models import Farm

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'farmer', 'primary_crop', 'size_hectares', 'location', 'created_at']
    list_filter = ['primary_crop', 'created_at']
    search_fields = ['name', 'farmer__username', 'location']
    
    fieldsets = (
        (None, {
            'fields': ('farmer', 'name', 'location', 'size_hectares', 'primary_crop')
        }),
        ('Optional Information', {
            'fields': ('gps_coordinates',),
            'classes': ('collapse',),
        }),
    )