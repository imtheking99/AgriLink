from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Crop, UserProfile

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

class RegistrationForm(UserCreationForm):

    USER_TYPES = (
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
    )

    user_type = forms.ChoiceField(
        choices=USER_TYPES,
        widget=forms.RadioSelect(attrs={'class': 'user-type-radio'})
    )

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter email address'
    }))

    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Phone Number'
    }))

    district = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'District'
    }))

    address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-input',
        'rows': 3,
        'placeholder': 'Address'
    }))

    farm_size = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Farm Size'
        })
    )

    main_crop = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Main Crop'
        })
    )

    business_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Business Name'
        })
    )

    buying_interest = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buying Interest'
        })
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'user_type',
            'phone',
            'district',
            'address',
            'farm_size',
            'main_crop',
            'business_name',
            'buying_interest',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type'],
                phone=self.cleaned_data['phone'],
                district=self.cleaned_data['district'],
                address=self.cleaned_data['address'],
                farm_size=self.cleaned_data['farm_size'],
                main_crop=self.cleaned_data['main_crop'],
                business_name=self.cleaned_data['business_name'],
                buying_interest=self.cleaned_data['buying_interest'],
            )

        return user

class FarmerLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter password'
    }))
