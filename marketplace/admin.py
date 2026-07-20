from django.contrib import admin
from .models import FertilizerProduct, Order, OrderItem

@admin.register(FertilizerProduct)
class FertilizerProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'npk_ratio', 'price_per_bag', 'stock_quantity', 'is_active']
    list_filter = ['npk_ratio', 'is_active', 'brand']
    search_fields = ['name', 'brand', 'npk_ratio']
    list_editable = ['price_per_bag', 'stock_quantity', 'is_active']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'farmer', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['farmer__username', 'payment_reference']
    inlines = [OrderItemInline]