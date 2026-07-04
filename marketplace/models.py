from django.db import models
from django.contrib.auth.models import User

class Bid(models.Model):
    # Status සඳහා තෝරාගත හැකි විකල්ප (Choices)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    # Crop එක (Foreign Key) - agrilink app එකේ තියෙන Crop model එකට සම්බන්ධ කර ඇත
    crop = models.ForeignKey('Pages.Crop', on_delete=models.CASCADE, related_name='bids')
    
    # Buyer (Foreign Key) - Django User model එකට සම්බන්ධ කර ඇත
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    
    # Bid Amount (ගණන)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status (Pending / Accepted / Rejected)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    
    # සාදපු දිනය සහ වේලාව auto එකතු වීමට
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid {self.bid_amount} by {self.buyer.username} for {self.crop}"


class Appointment(models.Model):
    # Farmer (Foreign Key)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farmer_appointments')
    
    # Buyer (Foreign Key)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_appointments')
    
    # Date & Time (දිනය සහ වේලාව)
    date_time = models.DateTimeField()
    
    # Location / Note
    location_note = models.TextField()

    def __str__(self):
        return f"Appointment: {self.farmer.username} & {self.buyer.username} on {self.date_time}"