from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from Pages.models import Crop
from .models import Bid, SavedSearch
from .forms import BidForm

# Buyer Dashboard - Premium UI with sidebar
@login_required
def buyer_dashboard(request):
    user = request.user
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # All bids for this buyer
    all_bids = Bid.objects.filter(buyer=user).select_related('crop', 'crop__farmer')

    # Stats
    active_bids_count = all_bids.filter(status='pending').count()
    active_bids_this_week = all_bids.filter(status='pending', created_at__gte=week_ago).count()

    won_bids_count = all_bids.filter(status='won').count()
    won_bids_this_month = all_bids.filter(status='won', created_at__gte=month_ago).count()

    saved_searches = SavedSearch.objects.filter(buyer=user)
    saved_searches_count = saved_searches.count()

    total_spent = all_bids.filter(status='won').aggregate(total=Sum('amount'))['total'] or 0

    # Recent active bids (for the list)
    recent_bids = all_bids.order_by('-created_at')[:10]

    # Trending crops (most bid-on crops system-wide)
    trending_crops = Crop.objects.annotate(
        bid_count=Count('bids')
    ).order_by('-bid_count')[:5]

    context = {
        'active_bids_count': active_bids_count,
        'active_bids_this_week': active_bids_this_week,
        'won_bids_count': won_bids_count,
        'won_bids_this_month': won_bids_this_month,
        'saved_searches_count': saved_searches_count,
        'total_spent': total_spent,
        'recent_bids': recent_bids,
        'saved_searches': saved_searches[:6],
        'trending_crops': trending_crops,
        'bids': all_bids.order_by('-created_at'),
    }
    return render(request, 'buyer/buyer_dashboard.html', context)

# Crop Search and Filter
@login_required
def crop_search(request):
    crops = Crop.objects.all().select_related('farmer').order_by('-created_at')
    
    # GET parameters
    crop_name = request.GET.get('crop_name', '').strip()
    district = request.GET.get('district', '').strip()
    harvest_date = request.GET.get('harvest_date', '').strip()
    
    # Filtering logic
    if crop_name:
        crops = crops.filter(crop_name__icontains=crop_name)
    if district:
        crops = crops.filter(district__icontains=district)
    if harvest_date:
        crops = crops.filter(expected_harvest_date=harvest_date)
        
    context = {
        'crops': crops,
        'crop_name': crop_name,
        'district': district,
        'harvest_date': harvest_date,
    }
    return render(request, 'buyer/crop_search.html', context)

# Crop Details and Bid Placement
@login_required
def crop_detail(request, pk):
    crop = get_object_or_404(Crop, pk=pk)
    bids = crop.bids.all().select_related('buyer').order_by('-amount', '-created_at')
    
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.buyer = request.user
            bid.crop = crop
            bid.save()
            messages.success(request, f"Your bid of LKR {bid.amount} has been successfully placed on {crop.crop_name}!")
            return redirect('crop_detail', pk=pk)
        else:
            messages.error(request, "Failed to place bid. Please enter a valid positive amount.")
    else:
        form = BidForm()
        
    context = {
        'crop': crop,
        'bids': bids,
        'form': form,
    }
    return render(request, 'buyer/crop_detail.html', context)

# Save a search
@login_required
def save_search(request):
    if request.method == 'POST':
        crop_name = request.POST.get('crop_name', '').strip()
        district = request.POST.get('district', '').strip()
        if crop_name:
            SavedSearch.objects.create(
                buyer=request.user,
                crop_name=crop_name,
                district=district,
            )
            messages.success(request, f"Search for '{crop_name}' saved!")
        else:
            messages.error(request, "Crop name is required to save a search.")
    return redirect('buyer_dashboard')

# Delete a saved search
@login_required
def delete_saved_search(request, pk):
    search = get_object_or_404(SavedSearch, pk=pk, buyer=request.user)
    search.delete()
    messages.success(request, "Saved search removed.")
    return redirect('buyer_dashboard')

# Quick search redirect
@login_required
def quick_search(request):
    q = request.GET.get('q', '').strip()
    if q:
        return redirect(f"/buyer/search/?crop_name={q}")
    return redirect('crop_search')
