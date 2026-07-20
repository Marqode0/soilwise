from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import AgentProfile, Kit, AgentApplication, LabTechApplication, LabTechContract, CollectionRecord, WithdrawalRequest
from .forms import AgentApplicationForm, LabTechApplicationForm
from soiltests.models import SoilSample
from notifications.models import Notification
import datetime

User = get_user_model()

# ===== AGENT VIEWS =====

@login_required
def agent_dashboard(request):
    try:
        profile = AgentProfile.objects.get(user=request.user)
    except AgentProfile.DoesNotExist:
        if request.user.role == 'agent':
            profile = AgentProfile.objects.create(
                user=request.user,
                tier='bronze'
            )
        else:
            messages.error(request, 'You are not registered as an agent.')
            return redirect('home')
    
    agent_id = f"AGENT{str(request.user.id).zfill(5)}"
    display_name = profile.display_name if profile.display_name else request.user.username
    
    # Get samples assigned to this agent
    pending_samples = SoilSample.objects.filter(
        agent=request.user,
        status='pending'
    ).order_by('-created_at')
    
    # Get samples that have been collected (status = 'collected')
    collected_samples = SoilSample.objects.filter(
    agent=request.user,
    status__in=['collected', 'in_transit']
    ).order_by('-collection_date')
    
    # Get samples that are ready for collection (pending)
    ready_for_collection = SoilSample.objects.filter(
        agent=request.user,
        status='pending'
    ).order_by('-created_at')
    
    # Get all samples for this agent
    all_samples = SoilSample.objects.filter(agent=request.user).order_by('-created_at')
    kits = Kit.objects.filter(assigned_to=request.user)
    
    # Calculate commission ONLY for collected samples
    commission_per_sample = 200
    collected_count = collected_samples.count()
    total_earnings = collected_count * commission_per_sample
    
    # Update profile earnings
    profile.total_earnings = total_earnings
    profile.total_commission_earned = total_earnings
    profile.save()
    
    withdrawal_minimum = 5000
    can_withdraw = total_earnings >= withdrawal_minimum
    
    context = {
        'profile': profile,
        'display_name': display_name,
        'agent_id': agent_id,
        'kits': kits,
        'pending_samples': pending_samples,
        'collected_samples': collected_samples,
        'ready_for_collection': ready_for_collection,
        'all_samples': all_samples,
        'total_samples': all_samples.count(),
        'pending_count': pending_samples.count(),
        'collected_count': collected_count,
        'total_earnings': total_earnings,
        'commission_per_sample': commission_per_sample,
        'withdrawal_minimum': withdrawal_minimum,
        'can_withdraw': can_withdraw,
    }
    return render(request, 'agents/dashboard.html', context)

@login_required
def accept_collection(request, sample_id):
    try:
        profile = AgentProfile.objects.get(user=request.user)
    except AgentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as an agent.')
        return redirect('home')
    
    sample = get_object_or_404(SoilSample, id=sample_id)
    
    if sample.agent != request.user:
        messages.error(request, 'You are not assigned to this sample.')
        return redirect('agent_dashboard')
    
    if sample.status == 'collected':
        messages.info(request, 'This sample has already been collected.')
        return redirect('agent_dashboard')
    
    if request.method == 'POST':
        location = request.POST.get('location')
        gps = request.POST.get('gps_coordinates')
        notes = request.POST.get('notes')
        signature = request.POST.get('signature')
        
        if not location:
            messages.error(request, 'Please enter the collection location.')
            return redirect('accept_collection', sample_id=sample_id)
        
        if not signature:
            messages.error(request, 'Please sign to confirm collection.')
            return redirect('accept_collection', sample_id=sample_id)
        
        sample.status = 'collected'
        sample.collection_date = timezone.now()
        sample.save()
        
        CollectionRecord.objects.create(
            sample=sample,
            agent=request.user,
            collected_at=timezone.now(),
            location=location,
            gps_coordinates=gps,
            notes=notes,
            signature=signature
        )
        
        profile.total_collections += 1
        profile.total_commission_earned += 200
        profile.total_earnings += 200
        profile.save()
        
        Notification.objects.create(
            user=sample.farm.farmer,
            title='✅ Sample Collected',
            message=f'Your sample {sample.barcode} has been collected by {request.user.username}. It is now on its way to the lab.'
        )
        
        messages.success(request, f'Sample {sample.barcode} has been physically collected! +₦200 commission earned.')
        return redirect('agent_dashboard')
    
    context = {
        'sample': sample,
    }
    return render(request, 'agents/collect_sample.html', context)

@login_required
def collect_sample_form(request, sample_id):
    try:
        profile = AgentProfile.objects.get(user=request.user)
    except AgentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as an agent.')
        return redirect('home')
    
    sample = get_object_or_404(SoilSample, id=sample_id)
    
    if sample.agent != request.user:
        messages.error(request, 'You are not assigned to this sample.')
        return redirect('agent_dashboard')
    
    if sample.status == 'collected':
        messages.info(request, 'This sample has already been collected.')
        return redirect('agent_dashboard')
    
    context = {
        'sample': sample,
    }
    return render(request, 'agents/collect_sample.html', context)

@login_required
def apply_agent(request):
    if hasattr(request.user, 'agent_application'):
        application = request.user.agent_application
        
        if application.status == 'pending':
            messages.info(request, 'Your agent application is currently being reviewed. You will be notified once a decision is made.')
            return redirect('home')
        elif application.status == 'approved':
            messages.success(request, 'You are already an approved agent!')
            return redirect('agent_dashboard')
        elif application.status == 'rejected':
            messages.error(request, f'Your agent application was rejected. Reason: {application.rejection_message or "No reason provided."}')
            return redirect('home')
    
    if request.method == 'POST':
        form = AgentApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = 'pending'
            application.save()
            messages.success(request, 'Application submitted successfully! You will be notified once reviewed.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AgentApplicationForm()
    
    return render(request, 'agents/apply.html', {'form': form})

@login_required
def mark_in_transit(request, sample_id):
    try:
        profile = AgentProfile.objects.get(user=request.user)
    except AgentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as an agent.')
        return redirect('home')
    
    sample = get_object_or_404(SoilSample, id=sample_id)
    
    if sample.agent != request.user:
        messages.error(request, 'You are not assigned to this sample.')
        return redirect('agent_dashboard')
    
    if sample.status != 'collected':
        messages.error(request, 'This sample has not been collected yet.')
        return redirect('agent_dashboard')
    
    if request.method == 'POST':
        lab_tech_id = request.POST.get('lab_tech')
        
        if not lab_tech_id:
            messages.error(request, 'Please select a lab technician.')
            return redirect('mark_in_transit', sample_id=sample_id)
        
        lab_tech = get_object_or_404(User, id=lab_tech_id, role='lab_tech', is_approved=True)
        
        # Update sample
        sample.status = 'in_transit'
        sample.assigned_lab_tech = lab_tech
        sample.save()
        
        # Notify the selected lab tech
        Notification.objects.create(
            user=lab_tech,
            title='📦 Sample In Transit',
            message=f'Sample {sample.barcode} is on its way to you from {request.user.username}.'
        )
        
        messages.success(request, f'Sample {sample.barcode} marked as in transit! Assigned to {lab_tech.username}.')
        return redirect('agent_dashboard')
    
    # Get all approved lab techs
    lab_techs = User.objects.filter(role='lab_tech', is_approved=True)
    
    context = {
        'sample': sample,
        'lab_techs': lab_techs,
    }
    return render(request, 'agents/mark_in_transit.html', context)
# ===== LAB TECH VIEWS =====

@login_required
def apply_labtech(request):
    if hasattr(request.user, 'labtech_application'):
        application = request.user.labtech_application
        
        if application.status == 'pending':
            messages.info(request, 'Your lab technician application is currently being reviewed. You will be notified once a decision is made.')
            return redirect('home')
        elif application.status == 'approved':
            messages.success(request, 'Your lab technician application has been approved! Please sign your contract.')
            return redirect('contract')
        elif application.status == 'rejected':
            messages.error(request, f'Your lab technician application was rejected. Reason: {application.rejection_message or "No reason provided."}')
            return redirect('home')
    
    if request.method == 'POST':
        form = LabTechApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = 'pending'
            application.save()
            messages.success(request, 'Lab Tech application submitted successfully! You will be notified once reviewed.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LabTechApplicationForm()
    
    return render(request, 'agents/apply_labtech.html', {'form': form})

@login_required
def contract(request):
    contract_obj = LabTechContract.objects.filter(user=request.user).first()
    
    if contract_obj and contract_obj.status == 'completed':
        messages.success(request, 'Your contract has been finalized! You can now start working as a lab technician.')
        return redirect('lab_dashboard')
    
    if contract_obj and contract_obj.status == 'pending':
        messages.info(request, 'Your contract is awaiting admin approval. Please wait up to 24 hours.')
        return redirect('home')
    
    if contract_obj and contract_obj.status == 'approved':
        messages.success(request, 'Your contract has been approved! You can now start working as a lab technician.')
        return redirect('lab_dashboard')
    
    if contract_obj and contract_obj.status == 'rejected':
        messages.error(request, f'Your contract was rejected. Reason: {contract_obj.admin_notes or "No reason provided."}')
        return redirect('home')
    
    if request.method == 'POST':
        agree = request.POST.get('agree')
        signature = request.POST.get('signature')
        
        if not agree:
            messages.error(request, 'You must agree to the terms and conditions.')
            return redirect('contract')
        
        if not signature:
            messages.error(request, 'Please type your full name as signature.')
            return redirect('contract')
        
        contract_obj = LabTechContract.objects.create(
            user=request.user,
            contract_text=f'''
Lab Technician Employment Contract
Date: {datetime.datetime.now().strftime("%Y-%m-%d")}
Employee: {signature}
Status: Signed and submitted for approval
''',
            signed_at=datetime.datetime.now(),
            status='pending'
        )
        
        Notification.objects.create(
            user=request.user,
            title='📄 Contract Signed',
            message=f'Your lab technician contract has been signed and submitted for admin approval. You will be notified within 24 hours.'
        )
        
        messages.success(request, 'Contract signed successfully! Please wait for admin approval (up to 24 hours).')
        return redirect('home')
    
    context = {
        'contract_date': datetime.datetime.now().strftime("%B %d, %Y"),
    }
    return render(request, 'agents/contract.html', context)

@login_required
def approve_contract(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to approve contracts.')
        return redirect('home')
    
    contract_obj = get_object_or_404(LabTechContract, user_id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes')
        
        if action == 'approve':
            contract_obj.status = 'approved'
            contract_obj.approved_at = timezone.now()
            contract_obj.admin_notes = admin_notes
            contract_obj.save()
            
            Notification.objects.create(
                user=contract_obj.user,
                title='✅ Contract Approved!',
                message=f'Your lab technician contract has been approved by admin. You can now start working!'
            )
            
            messages.success(request, f'Contract for {contract_obj.user.username} approved successfully.')
            return redirect('admin:agents_labtechcontract_changelist')
        
        elif action == 'reject':
            contract_obj.status = 'rejected'
            contract_obj.admin_notes = admin_notes
            contract_obj.save()
            
            Notification.objects.create(
                user=contract_obj.user,
                title='❌ Contract Rejected',
                message=f'Your lab technician contract was rejected. Reason: {admin_notes or "No reason provided."}'
            )
            
            messages.success(request, f'Contract for {contract_obj.user.username} rejected.')
            return redirect('admin:agents_labtechcontract_changelist')
    
    context = {
        'contract': contract_obj,
    }
    return render(request, 'agents/contract_review.html', context)

@login_required
def my_kits(request):
    try:
        profile = AgentProfile.objects.get(user=request.user)
    except AgentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as an agent.')
        return redirect('home')
    
    kits = Kit.objects.filter(assigned_to=request.user)
    
    context = {
        'kits': kits,
        'total_kits': kits.count(),
        'used_kits': kits.filter(is_used=True).count(),
        'available_kits': kits.filter(is_used=False).count(),
    }
    return render(request, 'agents/my_kits.html', context)

@login_required
def my_collections(request):
    try:
        profile = AgentProfile.objects.get(user=request.user)
    except AgentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as an agent.')
        return redirect('home')
    
    # Get all samples collected by this agent
    collections = SoilSample.objects.filter(
        agent=request.user,
        status__in=['collected', 'in_transit', 'at_lab', 'testing', 'results_ready', 'completed']
    ).order_by('-collection_date')
    
    context = {
        'collections': collections,
        'total_collections': collections.count(),
    }
    return render(request, 'agents/my_collections.html', context)

@login_required
def request_withdrawal(request):
    try:
        profile = AgentProfile.objects.get(user=request.user)
    except AgentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as an agent.')
        return redirect('home')
    
    withdrawal_minimum = 5000
    
    if profile.total_earnings < withdrawal_minimum:
        messages.error(request, f'Minimum withdrawal is ₦{withdrawal_minimum}. You have ₦{profile.total_earnings}.')
        return redirect('agent_dashboard')
    
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        account_name = request.POST.get('account_name')
        
        if amount < withdrawal_minimum:
            messages.error(request, f'Minimum withdrawal is ₦{withdrawal_minimum}.')
            return redirect('agent_dashboard')
        
        if amount > profile.total_earnings:
            messages.error(request, f'You only have ₦{profile.total_earnings} available.')
            return redirect('agent_dashboard')
        
        # Create withdrawal request
        WithdrawalRequest.objects.create(
            agent=request.user,
            amount=amount,
            bank_name=bank_name,
            bank_account_number=account_number,
            bank_account_name=account_name,
            status='pending'
        )
        
        # Deduct from earnings
        profile.pending_earnings += amount
        profile.total_earnings -= amount
        profile.save()
        
        messages.success(request, f'Withdrawal request of ₦{amount} submitted successfully! Admin will process it.')
        return redirect('agent_dashboard')
    
    context = {
        'profile': profile,
        'withdrawal_minimum': withdrawal_minimum,
    }
    return render(request, 'agents/withdraw.html', context)

@login_required
def withdrawal_history(request):
    try:
        profile = AgentProfile.objects.get(user=request.user)
    except AgentProfile.DoesNotExist:
        messages.error(request, 'You are not registered as an agent.')
        return redirect('home')
    
    withdrawals = WithdrawalRequest.objects.filter(agent=request.user).order_by('-created_at')
    
    context = {
        'withdrawals': withdrawals,
        'total_withdrawn': sum(w.amount for w in withdrawals if w.status == 'completed'),
        'pending_withdrawals': sum(w.amount for w in withdrawals if w.status == 'pending'),
    }
    return render(request, 'agents/withdrawal_history.html', context)