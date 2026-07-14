from django.urls import path
from django.contrib import admin
from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/add/', views.crop_create, name='crop_add'),
    path('farmer/edit/<int:pk>/', views.crop_update, name='crop_edit'),
    path('farmer/delete/<int:pk>/', views.crop_delete, name='crop_delete'),
    path('weather/', include (('weather.urls', 'weather'), namespace='weather')),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/export/', views.export_crops_report, name='export_reports'),
]


