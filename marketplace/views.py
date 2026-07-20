from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import FertilizerProduct, Order, OrderItem
from soiltests.models import SoilSample
import requests
import json
import uuid

@login_required
def marketplace(request, sample_id):
    sample = get_object_or_404(SoilSample, id=sample_id)
    
    # Ensure the sample belongs to the logged-in user
    if sample.farm.farmer != request.user:
        messages.error(request, 'You do not have permission to view this marketplace.')
        return redirect('home')
    
    # Check if result exists
    if not hasattr(sample, 'result'):
        messages.error(request, 'No test results available for this sample.')
        return redirect('farmer_dashboard', farmer_id=request.user.id)
    
    # Get recommendation data
    npk_ratio = sample.result.recommendations.get('npk_ratio', '15:15:15')
    bags_needed = int(sample.result.recommendations.get('bags_per_hectare', 2))
    farm_size = sample.farm.size_hectares
    total_bags_needed = int(bags_needed * farm_size)
    
    # Get products matching the NPK ratio
    products = FertilizerProduct.objects.filter(
        npk_ratio=npk_ratio,
        is_active=True
    )
    
    # Get existing cart items
    cart_items = []
    if 'cart' in request.session:
        cart_session = request.session.get('cart', {})
        for key, value in cart_session.items():
            if value.get('sample_id') == sample_id:
                product_id = value.get('product_id')
                quantity = value.get('quantity', 0)
                product = FertilizerProduct.objects.filter(id=product_id).first()
                if product:
                    cart_items.append({
                        'product': product,
                        'quantity': quantity,
                        'total': product.price_per_bag * quantity
                    })
    
    context = {
        'sample': sample,
        'npk_ratio': npk_ratio,
        'bags_needed': bags_needed,
        'farm_size': farm_size,
        'total_bags_needed': total_bags_needed,
        'products': products,
        'cart_items': cart_items,
        'cart_total': sum(item['total'] for item in cart_items),
    }
    return render(request, 'marketplace/marketplace.html', context)

@login_required
def add_to_cart(request, product_id, sample_id):
    product = get_object_or_404(FertilizerProduct, id=product_id)
    sample = get_object_or_404(SoilSample, id=sample_id)
    
    # Get quantity from form
    quantity = int(request.POST.get('quantity', 1))
    
    # Check stock
    if quantity > product.stock_quantity:
        messages.error(request, f'Sorry, only {product.stock_quantity} bags in stock.')
        return redirect('marketplace', sample_id=sample_id)
    
    # Add to cart session
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    cart = request.session.get('cart', {})
    cart_key = f"{product_id}_{sample_id}"
    
    if cart_key in cart:
        # Update quantity
        current_quantity = cart[cart_key]['quantity']
        new_quantity = current_quantity + quantity
        if new_quantity > product.stock_quantity:
            messages.error(request, f'Sorry, only {product.stock_quantity} bags in stock.')
            return redirect('marketplace', sample_id=sample_id)
        cart[cart_key]['quantity'] = new_quantity
    else:
        cart[cart_key] = {
            'product_id': product_id,
            'sample_id': sample_id,
            'quantity': quantity,
        }
    
    request.session['cart'] = cart
    messages.success(request, f'{quantity} bag(s) of {product.name} added to cart!')
    return redirect('marketplace', sample_id=sample_id)

@login_required
def view_cart(request):
    cart_items = []
    total = 0
    
    if 'cart' in request.session:
        cart = request.session.get('cart', {})
        for key, value in cart.items():
            product = FertilizerProduct.objects.filter(id=value.get('product_id')).first()
            if product:
                quantity = value.get('quantity', 1)
                item_total = product.price_per_bag * quantity
                total += item_total
                cart_items.append({
                    'key': key,
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'marketplace/cart.html', context)

@login_required
def remove_from_cart(request, cart_key):
    if 'cart' in request.session:
        cart = request.session.get('cart', {})
        if cart_key in cart:
            del cart[cart_key]
            request.session['cart'] = cart
            messages.success(request, 'Item removed from cart.')
    return redirect('view_cart')

@login_required
def checkout(request):
    if 'cart' not in request.session or not request.session.get('cart'):
        messages.error(request, 'Your cart is empty.')
        return redirect('view_cart')
    
    cart = request.session.get('cart', {})
    total = 0
    order_items_data = []
    
    for key, value in cart.items():
        product = FertilizerProduct.objects.filter(id=value.get('product_id')).first()
        if product:
            quantity = value.get('quantity', 1)
            item_total = product.price_per_bag * quantity
            total += item_total
            order_items_data.append({
                'product': product,
                'quantity': quantity,
                'price': product.price_per_bag,
                'total': item_total
            })
            # Reduce stock
            product.stock_quantity -= quantity
            product.save()
    
    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address')
        sample_id = request.POST.get('sample_id')
        sample = SoilSample.objects.filter(id=sample_id).first()
        
        if not delivery_address:
            messages.error(request, 'Please enter your delivery address.')
            return redirect('checkout')
        
        # Create order
        order = Order.objects.create(
            farmer=request.user,
            sample=sample,
            total_amount=total,
            status='pending',
            payment_reference=f"PAY{uuid.uuid4().hex[:10].upper()}",
            delivery_address=delivery_address
        )
        
        # Create order items
        for item in order_items_data:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
        
        # Clear cart
        request.session['cart'] = {}
        
        messages.success(request, f'Order #{order.id} placed successfully! Please proceed to payment.')
        return redirect('order_confirmation', order_id=order.id)
    
    sample_id = None
    if cart:
        first_item = next(iter(cart.values()))
        sample_id = first_item.get('sample_id')
    
    context = {
        'order_items': order_items_data,
        'total': total,
        'sample_id': sample_id,
    }
    return render(request, 'marketplace/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, farmer=request.user)
    return render(request, 'marketplace/confirmation.html', {'order': order})

@login_required
def initiate_order_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, farmer=request.user)
    
    # Amount in kobo (Paystack uses kobo)
    amount = int(order.total_amount)
    amount_in_kobo = amount * 100
    
    # Generate unique reference
    reference = f"ORD-{uuid.uuid4().hex[:10].upper()}"
    
    # Get user email
    email = request.user.email if request.user.email else f"{request.user.username}@soilwise.com"
    
    # Initialize transaction with Paystack
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "amount": amount_in_kobo,
        "reference": reference,
        "callback_url": request.build_absolute_uri(f"/marketplace/verify-order-payment/{reference}/"),
        "metadata": {
            "order_id": order.id,
            "user_id": request.user.id,
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()
        
        if response_data.get('status'):
            # Update order with payment reference
            order.payment_reference = reference
            order.save()
            
            # Redirect to Paystack payment page
            return redirect(response_data['data']['authorization_url'])
        else:
            messages.error(request, f"Payment initialization failed: {response_data.get('message', 'Unknown error')}")
            return redirect('order_confirmation', order_id=order.id)
    
    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('order_confirmation', order_id=order.id)

@login_required
def verify_order_payment(request, reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    
    try:
        response = requests.get(url, headers=headers)
        response_data = response.json()
        
        if response_data.get('status') and response_data['data']['status'] == 'success':
            # Update order status
            order = Order.objects.get(payment_reference=reference)
            order.status = 'paid'
            order.save()
            
            messages.success(request, 'Payment successful! Your order has been confirmed.')
            return redirect('order_confirmation', order_id=order.id)
        else:
            messages.error(request, 'Payment verification failed.')
            return redirect('order_confirmation', order_id=order.id)
    
    except Exception as e:
        messages.error(request, f"Verification error: {str(e)}")
        return redirect('order_confirmation', order_id=order.id)

@login_required
def my_orders(request):
    orders = Order.objects.filter(farmer=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'marketplace/my_orders.html', context)