from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Payment
from soiltests.models import SoilSample
import requests
import json
import uuid

@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/history.html', {'payments': payments})

@login_required
def initiate_payment(request, sample_id):
    sample = get_object_or_404(SoilSample, id=sample_id)
    
    # Amount in kobo (Paystack uses kobo)
    amount = 2000  # ₦2,000
    amount_in_kobo = amount * 100
    
    # Generate unique reference
    reference = f"PAY-{uuid.uuid4().hex[:10].upper()}"
    
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
        "callback_url": request.build_absolute_uri(f"/payments/verify/{reference}/"),
        "metadata": {
            "sample_id": sample.id,
            "user_id": request.user.id,
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()
        
        if response_data.get('status'):
            # Create payment record
            Payment.objects.create(
                user=request.user,
                sample=sample,
                amount=amount,
                reference=reference,
                status='pending',
                payment_method='card'
            )
            
            # Redirect to Paystack payment page
            return redirect(response_data['data']['authorization_url'])
        else:
            messages.error(request, f"Payment initialization failed: {response_data.get('message', 'Unknown error')}")
            return redirect('farmer_dashboard', farmer_id=request.user.id)
    
    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('farmer_dashboard', farmer_id=request.user.id)

@login_required
def verify_payment(request, reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    
    try:
        response = requests.get(url, headers=headers)
        response_data = response.json()
        
        if response_data.get('status') and response_data['data']['status'] == 'success':
            # Update payment status
            payment = Payment.objects.get(reference=reference)
            payment.status = 'completed'
            payment.paid_at = response_data['data']['paid_at']
            payment.save()
            
            # Update sample status (optional)
            sample = payment.sample
            if sample:
                sample.status = 'collected'
                sample.save()
            
            messages.success(request, 'Payment successful! Your test has been confirmed.')
            return redirect('farmer_dashboard', farmer_id=request.user.id)
        else:
            messages.error(request, 'Payment verification failed.')
            return redirect('farmer_dashboard', farmer_id=request.user.id)
    
    except Exception as e:
        messages.error(request, f"Verification error: {str(e)}")
        return redirect('farmer_dashboard', farmer_id=request.user.id)