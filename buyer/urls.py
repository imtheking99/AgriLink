from django.urls import path
from . import views

urlpatterns = [
    path('', views.buyer_dashboard, name='buyer_dashboard'),
    path('search/', views.crop_search, name='crop_search'),
    path('crop/<int:pk>/', views.crop_detail, name='crop_detail'),
    path('save-search/', views.save_search, name='save_search'),
    path('delete-search/<int:pk>/', views.delete_saved_search, name='delete_saved_search'),
    path('quick-search/', views.quick_search, name='quick_search'),
]
