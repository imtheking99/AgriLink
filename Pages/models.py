from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Crop(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crops')
    crop_name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)  # CharField to support units (e.g., '500 kg')
    district = models.CharField(max_length=100)
    expected_harvest_date = models.DateField()
    crop_image = models.ImageField(upload_to='crops/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='Active')
    crop_status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('sold', 'Sold'),
        ],
        default='available'
    )

    def __str__(self):
        return f"{self.crop_name} - {self.quantity} ({self.farmer.username})"


class WeatherAlert(models.Model):
    is_active = models.BooleanField(default=True)
    

class RecentActivity(models.Model):
    description = models.CharField(max_length=255)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description
class UserProfile(models.Model):
    USER_TYPES = (
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)

    phone = models.CharField(max_length=15)
    district = models.CharField(max_length=100)
    address = models.TextField()

    farm_size = models.CharField(max_length=100, blank=True)
    main_crop = models.CharField(max_length=100, blank=True)

    business_name = models.CharField(max_length=100, blank=True)
    buying_interest = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"
    
class Bid(models.Model):
    crop = models.ForeignKey(
        Crop,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    bid_date = models.DateTimeField(
        auto_now_add=True
    )

    accepted = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ['-amount']

    def __str__(self):
        return f"{self.buyer.username} - Rs.{self.amount} for {self.crop.crop_name}"
    
    #Notification model to notify farmers about new bids
    
class Notification(models.Model):
        user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

        message = models.CharField(max_length=255)

        is_read = models.BooleanField(
        default=False
    )

        created_at = models.DateTimeField(
        auto_now_add=True
    )

        def __str__(self):
            return f"{self.user.username} - {self.message}"
