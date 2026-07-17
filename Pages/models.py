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

    def __str__(self):
        return f"{self.crop_name} - {self.quantity} ({self.farmer.username})"
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