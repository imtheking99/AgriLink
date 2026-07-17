from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Crop, Bid
from .forms import CropForm, RegistrationForm, FarmerLoginForm


def home_view(request):
    return render(request, 'Pages/home.html')


def register_view(request):
    if request.user.is_authenticated:
        if request.user.userprofile.user_type == 'buyer':
            return redirect('buyer_dashboard')
        return redirect('farmer_dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            if user.userprofile.user_type == 'buyer':
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
        if request.user.userprofile.user_type == 'buyer':
            return redirect('buyer_dashboard')
        return redirect('farmer_dashboard')

    if request.method == 'POST':
        form = FarmerLoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.userprofile.user_type == 'buyer':
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
    if request.user.userprofile.user_type != 'farmer':
        return redirect('buyer_dashboard')

    crops = Crop.objects.filter(farmer=request.user).order_by('-created_at')
    return render(request, 'Pages/farmer_dashboard.html', {'crops': crops})


@login_required
def buyer_dashboard(request):
    if request.user.userprofile.user_type != 'buyer':
        return redirect('farmer_dashboard')

    crops = Crop.objects.all().order_by('-created_at')
    return render(request, 'Pages/buyer_dashboard.html', {'crops': crops})


@login_required
def crop_create(request):
    if request.user.userprofile.user_type != 'farmer':
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

    if request.user.userprofile.user_type != 'farmer':
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

    if request.user.userprofile.user_type != 'farmer':
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

@login_required
def bidding_page(request):

    if request.user.userprofile.user_type != 'buyer':
        return redirect('farmer_dashboard')

    crops = Crop.objects.all().order_by('-created_at')

    if request.method == "POST":

        crop_id = request.POST.get('crop_id')
        amount = request.POST.get('amount')

        crop = get_object_or_404(Crop, id=crop_id)

        Bid.objects.create(
            crop=crop,
            buyer=request.user,
            amount=amount
        )

        messages.success(request, "Your bid has been placed successfully!")

        return redirect('bidding_page')


    return render(
        request,
        'Pages/bidding.html',
        {'crops': crops}
    )

@login_required
def farmer_bids(request):

    if request.user.userprofile.user_type != 'farmer':
        return redirect('buyer_dashboard')

    crops = Crop.objects.filter(
        farmer=request.user
    )

    bids = Bid.objects.filter(
        crop__in=crops
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

    if request.user.userprofile.user_type != 'farmer':
        return redirect('buyer_dashboard')

    bid = get_object_or_404(Bid, id=bid_id)

    # Make sure this farmer owns this crop
    if bid.crop.farmer != request.user:
        messages.error(request, "You cannot accept this bid.")
        return redirect('farmer_bids')


    # Accept selected bid
    bid.accepted = True
    bid.save()


    # Optional: Reject other bids for the same crop
    Bid.objects.filter(
        crop=bid.crop
    ).exclude(
        id=bid.id
    ).update(
        accepted=False
    )


    messages.success(
        request,
        f"Bid from {bid.buyer.username} accepted successfully!"
    )


    return redirect('farmer_bids')

@login_required
def farmer_deals(request):

    if request.user.userprofile.user_type != 'farmer':
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