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

    def __str__(self):
        return f"{self.crop_name} - {self.quantity} ({self.farmer.username})"


class WeatherAlert(models.Model):
    is_active = models.BooleanField(default=True)
    

class RecentActivity(models.Model):
    description = models.CharField(max_length=255)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

