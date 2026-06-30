from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Crop

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['crop_name', 'quantity', 'district', 'expected_harvest_date', 'crop_image']
        widgets = {
            'crop_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter crop name (e.g. Paddy, Tomatoes)',
                'required': 'required'
            }),
            'quantity': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter quantity (e.g. 500 kg, 2 tons)',
                'required': 'required'
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter district (e.g. Anuradhapura)',
                'required': 'required'
            }),
            'expected_harvest_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'required': 'required'
            }),
            'crop_image': forms.ClearableFileInput(attrs={
                'class': 'form-input-file'
            }),
        }

class FarmerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter email address'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter username'
            }),
        }

class FarmerLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter password'
    }))
