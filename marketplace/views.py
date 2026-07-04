from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from Pages.models import Crop  # කලින් අපි දැක්කා Crop model එක තියෙන්නේ Pages එකේ කියලා
from .models import Bid, Appointment
from django.utils import timezone

# 1. Place Bid View (Buyer කෙනෙකුට bid එකක් දාන්න)
@login_required
def place_bid(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id)
    
    if request.method == 'POST':
        amount = request.POST.get('bid_amount')
        if amount:
            Bid.objects.create(
                crop=crop,
                buyer=request.user,
                bid_amount=amount,
                status='Pending'
            )
            return redirect('marketplace_history') # ඉවර වෙලා History පිටුවට යවනවා
            
    return render(request, 'marketplace/place_bid.html', {'crop': crop})

# 2. Manage Bids (Farmer කෙනෙකුට තමන්ගේ බෝග වලට ආපු bids බලන්න)
@login_required
def manage_bids(request):
    # Farmer ගේ බෝග වලට අදාළ bids විතරක් පෙන්නන්න (Crop model එකේ farmer කියලා field එකක් ඇති කියලා හිතලා)
    # ඔයාගේ Crop model එකේ farmer field එකේ නම වෙනස් නම් ඒක මෙතනට දාන්න (උදා: user, owner)
    farmer_bids = Bid.objects.filter(crop__farmer=request.user)
    
    if request.method == 'POST':
        bid_id = request.POST.get('bid_id')
        action = request.POST.get('action') # 'accept' හෝ 'reject'
        bid = get_object_or_404(Bid, id=bid_id, crop__farmer=request.user)
        
        if action == 'accept':
            bid.status = 'Accepted'
            bid.save()
            # Accept කරපු ගමන් Appointment එකක් schedule කරන්න ඒ පිටුවට redirect කරනවා
            return redirect('schedule_appointment', bid_id=bid.id)
        elif action == 'reject':
            bid.status = 'Rejected'
            bid.save()
            return redirect('manage_bids')

    return render(request, 'marketplace/manage_bids.html', {'bids': farmer_bids})

# 3. Schedule Appointment View (දිනය සහ වේලාව වෙන් කිරීම)
@login_required
def schedule_appointment(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    
    if request.method == 'POST':
        date_time = request.POST.get('date_time')
        note = request.POST.get('location_note')
        
        if date_time:
            Appointment.objects.create(
                farmer=bid.crop.farmer,
                buyer=bid.buyer,
                date_time=date_time,
                location_note=note
            )
            return redirect('marketplace_history')
            
    return render(request, 'marketplace/schedule_appointment.html', {'bid': bid})

# 4. History View (Farmer සහ Buyer දෙන්නටම තමන්ගේ හිස්ට්‍රිය බලන්න)
@login_required
def marketplace_history(request):
    # දැනට Login වෙලා ඉන්න කෙනා Buyer නම් එයා දාපු bids, Farmer නම් එයාට ආපු bids
    my_bids = Bid.objects.filter(buyer=request.user)
    
    # ඇපොයින්ට්මන්ට්ස් (දෙන්නටම අදාළ ඒවා)
    my_appointments = Appointment.objects.filter(farmer=request.user) | Appointment.objects.filter(buyer=request.user)
    
    context = {
        'my_bids': my_bids,
        'my_appointments': my_appointments
    }
    return render(request, 'marketplace/history.html', context)