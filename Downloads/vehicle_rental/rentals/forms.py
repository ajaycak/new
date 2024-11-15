# vehicle_rental/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Use default User model
from .models import VehicleRequest, Booking
from django.core.exceptions import ValidationError
import re
from django import forms
from django.contrib.auth.models import User

class CustomUserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.set_password(self.cleaned_data['password1'])
            user.save()
        return user


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'return_date']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
        }


class VehicleRequestForm(forms.ModelForm):
    class Meta:
        model = VehicleRequest
        fields = ['vehicle_type', 'model', 'price', 'owner_contact']
