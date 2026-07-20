from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.payment_history, name='payment_history'),
    path('initiate/<int:sample_id>/', views.initiate_payment, name='initiate_payment'),
    path('verify/<str:reference>/', views.verify_payment, name='verify_payment'),
]