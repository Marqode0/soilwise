from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.notification_history, name='notification_history'),
    # Add more URLs later if needed
]