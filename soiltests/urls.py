from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/<int:farmer_id>/', views.farmer_dashboard, name='farmer_dashboard'),
    path('request-test/', views.request_test, name='request_test'),
    path('test-result/<int:sample_id>/', views.test_result, name='test_result'),
    path('lab-dashboard/', views.lab_dashboard, name='lab_dashboard'),
    path('lab/upload/<int:sample_id>/', views.upload_test_result, name='upload_test_result'),
    path('lab/mark-at-lab/<int:sample_id>/', views.mark_at_lab, name='mark_at_lab'),
    path('lab/mark-testing/<int:sample_id>/', views.mark_testing, name='mark_testing'),
    path('pending-tests/', views.pending_tests, name='pending_tests'),
]