from django.contrib import admin
from .models import Crop

# Register your models here.
@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('crop_name', 'farmer', 'quantity', 'district', 'expected_harvest_date', 'created_at')
    list_filter = ('district', 'expected_harvest_date')
    search_fields = ('crop_name', 'farmer__username', 'district')

