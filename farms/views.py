from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Farm
from .forms import FarmForm

@login_required
def farm_list(request):
    farms = Farm.objects.filter(farmer=request.user)
    return render(request, 'farms/list.html', {'farms': farms})

@login_required
def add_farm(request):
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.farmer = request.user
            farm.save()
            messages.success(request, 'Farm added successfully!')
            return redirect('farm_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FarmForm()
    return render(request, 'farms/add_farm.html', {'form': form})