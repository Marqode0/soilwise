from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import User
from farms.models import Farm
from .models import SoilSample, TestResult
from .forms import SoilTestRequestForm
from agents.models import LabTechContract
from notifications.models import Notification
import uuid

def home(request):
    return render(request, 'soiltests/home.html')

@login_required
def farmer_dashboard(request, farmer_id):
    if request.user.id != farmer_id and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this dashboard.')
        return redirect('home')
    
    farmer = User.objects.get(id=farmer_id)
    farms = Farm.objects.filter(farmer=farmer)
    recent_tests = SoilSample.objects.filter(farm__in=farms).order_by('-created_at')[:5]
    
    context = {
        'farmer': farmer,
        'farms': farms,
        'recent_tests': recent_tests,
        'total_tests': recent_tests.count(),
    }
    return render(request, 'soiltests/dashboard.html', context)

@login_required
def request_test(request):
    if request.method == 'POST':
        form = SoilTestRequestForm(request.user, request.POST)
        if form.is_valid():
            soil_sample = form.save(commit=False)
            soil_sample.barcode = f"SW{str(uuid.uuid4()).replace('-', '')[:10].upper()}"
            soil_sample.status = 'pending'
            soil_sample.save()
            
            agent = soil_sample.agent
            if agent:
                Notification.objects.create(
                    user=agent,
                    title='📋 New Sample Collection Request',
                    message=f'''You have a new sample collection request from {request.user.username}.

Farm: {soil_sample.farm.name}
Location: {soil_sample.collection_location or soil_sample.farm.location}
Barcode: {soil_sample.barcode}

Please check your agent dashboard for details.'''
                )
                messages.success(request, f'Test requested successfully! Agent {agent.username} will collect your sample. Barcode: {soil_sample.barcode}')
            else:
                messages.success(request, f'Test requested successfully! Barcode: {soil_sample.barcode}')
            
            return redirect('farmer_dashboard', farmer_id=request.user.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SoilTestRequestForm(request.user)
    
    return render(request, 'soiltests/request_test.html', {'form': form})

@login_required
def test_result(request, sample_id):
    sample = get_object_or_404(SoilSample, id=sample_id)
    
    if sample.farm.farmer != request.user and request.user.role != 'lab_tech':
        messages.error(request, 'You do not have permission to view this test result.')
        return redirect('home')
    
    # If farmer is viewing and results are ready, mark as completed
    if sample.farm.farmer == request.user and sample.status == 'results_ready':
        sample.status = 'completed'
        sample.save()
    
    context = {
        'sample': sample,
    }
    return render(request, 'soiltests/test_result.html', context)

@login_required
def lab_dashboard(request):
    if request.user.role != 'lab_tech':
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('home')
    
    contract = LabTechContract.objects.filter(user=request.user).first()
    
    if not contract:
        messages.warning(request, 'Please sign your employment contract to start working.')
        return redirect('contract')
    
    if contract.status == 'pending':
        messages.info(request, 'Your contract is awaiting admin approval. Please wait up to 24 hours.')
        return redirect('home')
    
    if contract.status == 'rejected':
        messages.error(request, f'Your contract was rejected. Reason: {contract.admin_notes or "No reason provided."}')
        return redirect('home')
    
    # Show samples assigned to this lab tech
    samples = SoilSample.objects.filter(
        assigned_lab_tech=request.user,
        status__in=['in_transit', 'at_lab', 'testing']
    ).order_by('-created_at')
    
    context = {
        'samples': samples,
        'total_pending': samples.count(),
    }
    return render(request, 'soiltests/lab_dashboard.html', context)

@login_required
def upload_test_result(request, sample_id):
    if request.user.role != 'lab_tech':
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('home')
    
    sample = get_object_or_404(SoilSample, id=sample_id)
    
    if request.method == 'POST':
        nitrogen = request.POST.get('nitrogen')
        phosphorus = request.POST.get('phosphorus')
        potassium = request.POST.get('potassium')
        ph_level = request.POST.get('ph_level')
        organic_matter = request.POST.get('organic_matter')
        npk_ratio = request.POST.get('npk_ratio')
        bags = request.POST.get('bags')
        
        if organic_matter == '':
            organic_matter = None
        
        existing_result = TestResult.objects.filter(sample=sample).first()
        
        if existing_result:
            existing_result.nitrogen_ppm = nitrogen
            existing_result.phosphorus_ppm = phosphorus
            existing_result.potassium_ppm = potassium
            existing_result.ph_level = ph_level
            existing_result.organic_matter_percent = organic_matter
            existing_result.recommendations = {
                'npk_ratio': npk_ratio,
                'bags_per_hectare': bags,
                'notes': 'Apply at planting'
            }
            existing_result.tested_by = request.user
            existing_result.save()
            messages.success(request, f'Test results updated for {sample.barcode}')
        else:
            TestResult.objects.create(
                sample=sample,
                nitrogen_ppm=nitrogen,
                phosphorus_ppm=phosphorus,
                potassium_ppm=potassium,
                ph_level=ph_level,
                organic_matter_percent=organic_matter,
                recommendations={
                    'npk_ratio': npk_ratio,
                    'bags_per_hectare': bags,
                    'notes': 'Apply at planting'
                },
                tested_by=request.user
            )
            messages.success(request, f'Test results uploaded for {sample.barcode}')
        
        sample.status = 'results_ready'
        sample.save()
        
        return redirect('lab_dashboard')
    
    context = {
        'sample': sample,
    }
    return render(request, 'soiltests/upload_result.html', context)

@login_required
def mark_at_lab(request, sample_id):
    if request.user.role != 'lab_tech':
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('home')
    
    sample = get_object_or_404(SoilSample, id=sample_id)
    
    if sample.status != 'in_transit':
        messages.error(request, 'This sample has not been marked as in transit yet.')
        return redirect('lab_dashboard')
    
    sample.status = 'at_lab'
    sample.lab_received_date = timezone.now()
    sample.save()
    
    messages.success(request, f'Sample {sample.barcode} received at lab!')
    return redirect('lab_dashboard')

@login_required
def mark_testing(request, sample_id):
    if request.user.role != 'lab_tech':
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('home')
    
    sample = get_object_or_404(SoilSample, id=sample_id)
    
    if sample.status != 'at_lab':
        messages.error(request, 'This sample has not been marked as at lab yet.')
        return redirect('lab_dashboard')
    
    sample.status = 'testing'
    sample.save()
    
    messages.success(request, f'Sample {sample.barcode} is now being tested!')
    return redirect('lab_dashboard')

@login_required
def pending_tests(request):
    if request.user.role != 'lab_tech':
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('home')
    
    # Get all samples assigned to this lab tech that need attention
    pending = SoilSample.objects.filter(
        assigned_lab_tech=request.user,
        status__in=['in_transit', 'at_lab', 'testing']
    ).order_by('-created_at')
    
    context = {
        'pending': pending,
        'total_pending': pending.count(),
    }
    return render(request, 'soiltests/pending_tests.html', context)