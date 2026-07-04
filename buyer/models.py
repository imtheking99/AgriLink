from django.db import models
from django.contrib.auth.models import User
from Pages.models import Crop
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.
class Bid(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of {self.amount} on {self.crop.crop_name} by {self.buyer.username}"


class SavedSearch(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    crop_name = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        label = self.crop_name
        if self.district:
            label += f" · {self.district}"
        return label

    class Meta:
        ordering = ['-created_at']
