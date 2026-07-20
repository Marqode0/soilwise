from django.urls import path
from . import views

urlpatterns = [
    path('', views.farm_list, name='farm_list'),
    path('add/', views.add_farm, name='add_farm'),
]