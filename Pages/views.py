from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
import pandas as pd
import requests

from .models import Crop, WeatherAlert, RecentActivity, Bid, Notification, UserProfile
from .forms import CropForm, RegistrationForm, FarmerLoginForm


def home_view(request):
    city = 'Colombo'
    if request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.district:
        city = request.user.userprofile.district
        
    api_key = '1e74f142f97c2bdc20efeb4a44461208'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    context = {'weather_city': city}
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            context['temp'] = round(data['main']['temp'])
            context['condition'] = data['weather'][0]['main']
        else:
            context['temp'] = 28
            context['condition'] = 'Partly Cloudy'
    except Exception:
        context['temp'] = 28
        context['condition'] = 'Partly Cloudy'
        
    return render(request, 'Pages/home.html', context)


def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'buyer':
            return redirect('buyer_dashboard')
        return redirect('farmer_dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            if hasattr(user, 'userprofile') and user.userprofile.user_type == 'buyer':
                messages.success(request, f"Welcome to AgriLink, {user.username}! Your buyer account has been created.")
                return redirect('buyer_dashboard')
            else:
                messages.success(request, f"Welcome to AgriLink, {user.username}! Your farmer account has been created.")
                return redirect('farmer_dashboard')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'Pages/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'buyer':
            return redirect('buyer_dashboard')
        return redirect('farmer_dashboard')

    if request.method == 'POST':
        form = FarmerLoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_superuser:
                messages.success(request, f"Welcome back, Admin {user.username}!")
                return redirect('admin_dashboard')
            elif hasattr(user, 'userprofile') and user.userprofile.user_type == 'buyer':
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('buyer_dashboard')
            else:
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('farmer_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = FarmerLoginForm()

    return render(request, 'Pages/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')


@login_required
def farmer_dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'user_type': 'farmer',
            'phone': '0771234567',
            'district': 'Colombo',
            'address': 'Sri Lanka'
        }
    )
    if profile.user_type != 'farmer':
        return redirect('buyer_dashboard')

    crops = Crop.objects.filter(farmer=request.user).order_by('-created_at')
    weather_city = crops.first().district if (crops.exists() and crops.first().district) else profile.district
    weather_context = {'weather_city': weather_city}

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={weather_city}&appid=1e74f142f97c2bdc20efeb4a44461208&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            weather_context['weather_data'] = data
            weather_context['weather_description'] = data['weather'][0]['description']
        else:
            weather_context['weather_error'] = 'Weather service unavailable.'
    except Exception:
        weather_context['weather_error'] = 'Weather service unavailable.'

    return render(request, 'Pages/farmer_dashboard.html', {'crops': crops, **weather_context})


@login_required
def buyer_dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'user_type': 'buyer',
            'phone': '0771234567',
            'district': 'Colombo',
            'address': 'Sri Lanka'
        }
    )
    if profile.user_type != 'buyer':
        return redirect('farmer_dashboard')

    crops = Crop.objects.filter(
        crop_status='available'
    ).order_by('-created_at')
    return render(request, 'Pages/buyer_dashboard.html', {'crops': crops})


@login_required
def crop_create(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'farmer':
        return redirect('buyer_dashboard')

    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES)

        if form.is_valid():
            crop = form.save(commit=False)
            crop.farmer = request.user
            crop.save()
            messages.success(request, f"Crop '{crop.crop_name}' registered successfully!")
            return redirect('farmer_dashboard')
        else:
            messages.error(request, "Failed to register crop. Please check the details.")
    else:
        form = CropForm()

    return render(request, 'Pages/crop_form.html', {'form': form, 'action': 'Add'})


@login_required
def crop_update(request, pk):
    crop = get_object_or_404(Crop, pk=pk)

    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'farmer':
        return redirect('buyer_dashboard')

    if crop.farmer != request.user:
        messages.error(request, "Access denied. You can only edit your own crops.")
        return redirect('farmer_dashboard')

    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES, instance=crop)

        if form.is_valid():
            form.save()
            messages.success(request, f"Crop '{crop.crop_name}' updated successfully!")
            return redirect('farmer_dashboard')
        else:
            messages.error(request, "Failed to update crop. Please check the details.")
    else:
        form = CropForm(instance=crop)

    return render(request, 'Pages/crop_form.html', {'form': form, 'action': 'Edit', 'crop': crop})


@login_required
def crop_delete(request, pk):
    crop = get_object_or_404(Crop, pk=pk)

    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'farmer':
        return redirect('buyer_dashboard')

    if crop.farmer != request.user:
        messages.error(request, "Access denied. You can only delete your own crops.")
        return redirect('farmer_dashboard')

    if request.method == 'POST':
        crop_name = crop.crop_name
        crop.delete()
        messages.success(request, f"Crop '{crop_name}' deleted successfully.")
        return redirect('farmer_dashboard')

    return render(request, 'Pages/crop_confirm_delete.html', {'crop': crop})


def weather_index(request):
    city = request.GET.get('city', 'Colombo')
    api_key = '1e74f142f97c2bdc20efeb4a44461208'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    context = {'city': city}
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            context['weather'] = data
            desc = data['weather'][0]['description'].lower()
            
            # Decide class and icon
            if 'clear' in desc:
                context['condition_class'] = 'sunny'
                context['weather_icon'] = 'fa-sun'
            elif any(w in desc for w in ['rain', 'drizzle', 'storm']):
                context['condition_class'] = 'rainy'
                context['weather_icon'] = 'fa-cloud-showers-heavy'
            else:
                context['condition_class'] = 'cloudy'
                context['weather_icon'] = 'fa-cloud'
            
            # Alerts Logic
            if data['main']['temp'] > 30:
                context['alerts'] = ["High heat alert! Protect your crops."]
            elif 'rain' in desc:
                context['alerts'] = ["Rain expected! Ensure proper drainage."]
        else:
            context['error'] = 'City not found!'
    except:
        context['error'] = 'Service unavailable!'
        
    return render(request, 'weather/weather.html', context)

#Admin
#@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    total_users = User.objects.count()
    active_crops = Crop.objects.filter(status='Active').count()
    active_weather = WeatherAlert.objects.filter(is_active=True).count()
    recent_actions = RecentActivity.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'active_crops': active_crops,
        'active_weather': active_weather,
        'recent_actions': recent_actions,
    }
    return render(request, 'Pages/admin_panel.html', context)

    #export report
def export_crops_report(request):
    
    crops = Crop.objects.all().values('crop_name', 'quantity', 'district', 'expected_harvest_date')
    df = pd.DataFrame(list(crops))
    
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="AgriLink_Report.xlsx"'
    
    df.to_excel(response, index=False)
    return response
@login_required
def bidding_page(request):

    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'buyer':
        return redirect('farmer_dashboard')

    crops = Crop.objects.filter(
    crop_status='available'
    ).order_by('-created_at')


    if request.method == "POST":

        crop_id = request.POST.get('crop_id')
        amount = request.POST.get('amount')

        crop = get_object_or_404(
        Crop,
        id=crop_id,
        crop_status='available'
)


        Bid.objects.create(
            crop=crop,
            buyer=request.user,
            amount=amount
        )


        # Notify farmer
        Notification.objects.create(
            user=crop.farmer,
            message=f"{request.user.username} placed a bid of Rs.{amount} for your {crop.crop_name}"
        )


        messages.success(
            request,
            "Your bid has been placed successfully!"
        )


        return redirect('bidding_page')


    return render(
        request,
        'Pages/bidding.html',
        {
            'crops': crops
        }
    )

@login_required
def farmer_bids(request):

    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'farmer':
        return redirect('buyer_dashboard')

    crops = Crop.objects.filter(
        farmer=request.user
    )

    bids = Bid.objects.filter(
        crop__in=crops,
        accepted=False
        ).order_by('-amount')


    return render(
        request,
        'Pages/farmer_bids.html',
        {
            'bids': bids
        }
    )

@login_required
def accept_bid(request, bid_id):

    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'farmer':
        return redirect('buyer_dashboard')

    bid = get_object_or_404(Bid, id=bid_id)

    # Make sure this farmer owns this crop
    if bid.crop.farmer != request.user:
        messages.error(request, "You cannot accept this bid.")
        return redirect('farmer_bids')


    # Accept selected bid
    bid.accepted = True
    bid.save()

    # Mark crop as sold
    bid.crop.crop_status = 'sold'
    bid.crop.save()

     # Optional: Reject other bids for the same crop
    Bid.objects.filter(
        crop=bid.crop
    ).exclude(
        id=bid.id
    ).update(
        accepted=False
    )

    # Notify buyer
    Notification.objects.create(
        user=bid.buyer,
        message=f"Your bid for {bid.crop.crop_name} has been accepted by {request.user.username}"
)
    messages.success(
        request,
        f"Bid from {bid.buyer.username} accepted successfully!"
    )


    return redirect('farmer_bids')

@login_required
def farmer_deals(request):

    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'farmer':
        return redirect('buyer_dashboard')


    deals = Bid.objects.filter(
        crop__farmer=request.user,
        accepted=True
    ).order_by('-bid_date')


    return render(
        request,
        'Pages/farmer_deals.html',
        {
            'deals': deals
        }
    )
