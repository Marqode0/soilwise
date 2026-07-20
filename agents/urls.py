from django.urls import path
from . import views

urlpatterns = [
    # Agent URLs
    path('dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('accept/<int:sample_id>/', views.accept_collection, name='accept_collection'),
    path('collect/<int:sample_id>/', views.collect_sample_form, name='collect_sample_form'),
    path('apply/', views.apply_agent, name='apply_agent'),
    path('withdraw/', views.request_withdrawal, name='request_withdrawal'),
    path('mark-in-transit/<int:sample_id>/', views.mark_in_transit, name='mark_in_transit'),
    
    # Lab Tech URLs
    path('apply-labtech/', views.apply_labtech, name='apply_labtech'),
    path('contract/', views.contract, name='contract'),
    path('contract-approve/<int:user_id>/', views.approve_contract, name='approve_contract'),
    path('my-kits/', views.my_kits, name='my_kits'),
    path('my-collections/', views.my_collections, name='my_collections'),
    path('withdrawal-history/', views.withdrawal_history, name='withdrawal_history'),
]