from django.urls import path
from . import views

urlpatterns = [
    path('crop/<int:crop_id>/bid/', views.place_bid, name='place_bid'),
    path('bids/manage/', views.manage_bids, name='manage_bids'),
    path('bid/<int:bid_id>/accept/', views.schedule_appointment, name='schedule_appointment'),
    path('history/', views.marketplace_history, name='marketplace_history'),
]