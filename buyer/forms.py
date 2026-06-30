from django import forms
from .models import Bid

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your bid amount (e.g. 15000.00)',
                'min': '0.01',
                'step': '0.01',
                'required': 'required'
            }),
        }
        labels = {
            'amount': 'Bid Amount (LKR)',
        }
