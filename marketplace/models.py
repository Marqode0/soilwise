from django.db import models
from accounts.models import User
from soiltests.models import SoilSample

class FertilizerProduct(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    npk_ratio = models.CharField(max_length=20, help_text="e.g., 15:15:15")
    price_per_bag = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    stock_quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='fertilizers/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.npk_ratio} (₦{self.price_per_bag})"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    sample = models.ForeignKey(SoilSample, on_delete=models.SET_NULL, null=True, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    delivery_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.farmer.username} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(FertilizerProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of purchase
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} - ₦{self.price}"
    
    @property
    def total(self):
        return self.price * self.quantity