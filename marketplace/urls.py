from django.urls import path
from . import views

urlpatterns = [
    path('<int:sample_id>/', views.marketplace, name='marketplace'),
    path('add-to-cart/<int:product_id>/<int:sample_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<str:cart_key>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('initiate-order-payment/<int:order_id>/', views.initiate_order_payment, name='initiate_order_payment'),
    path('verify-order-payment/<str:reference>/', views.verify_order_payment, name='verify_order_payment'),
    path('my-orders/', views.my_orders, name='my_orders'),  # ADD THIS
]