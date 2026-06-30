from django.contrib import admin
from .models import Bid, SavedSearch

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('crop', 'buyer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'crop__district')
    search_fields = ('crop__crop_name', 'buyer__username', 'crop__district')
    list_editable = ('status',)

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'crop_name', 'district', 'created_at')
    search_fields = ('crop_name', 'district', 'buyer__username')
