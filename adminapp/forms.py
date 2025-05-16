from django import forms
from django.contrib.auth.models import User
from .models import Cuisine, Driver

class Cuisine_Form(forms.ModelForm):
    
    class Meta:
        model = Cuisine
        fields = '__all__'
        widgets = {
            'cuisine_name': forms.TextInput(attrs={
                'class': 'form-control rounded p-2 border border-gray-300',
                'placeholder': 'Enter cuisine name'
            }),
            'cuisine_description': forms.Textarea(attrs={
                'class': 'form-control rounded p-2 border border-gray-300',
                'rows': 3,
                'placeholder': 'Enter a short description'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control rounded p-2 border border-gray-300'
            }),
            'region': forms.Select(attrs={
                'class': 'form-control rounded p-2 border border-gray-300'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control rounded p-2 border border-gray-300',
                'placeholder': 'Price in ₹'
            }),
            'time': forms.NumberInput(attrs={
                'class': 'form-control rounded p-2 border border-gray-300',
                'placeholder': 'Time in minutes'
            }),
            'cuisine_image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
        }

class DriverForm(forms.ModelForm):
    username = forms.CharField(
        max_length=16,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded p-2 border border-gray-300',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded p-2 border border-gray-300',
            'placeholder': 'Password'
        })
    )

    class Meta:
        model = Driver
        fields = ['username', 'password', 'driver_name', 'gender', 'mobile_number', 'driver_image']
        widgets = {
            'driver_name': forms.TextInput(attrs={
                'class': 'form-control rounded p-2 border border-gray-300',
                'placeholder': 'Driver name'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control rounded p-2 border border-gray-300'
            }),
            'mobile_number': forms.NumberInput(attrs={
                'class': 'form-control rounded p-2 border border-gray-300',
                'placeholder': 'Mobile number'
            }),
            'driver_image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
        }

    def save(self, commit=True):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        # Create user
        user = User.objects.create_user(username=username)
        user.set_password(password)
        user.save()

        # Create driver profile
        driver = super().save(commit=False)
        driver.user = user
        driver.username = username  # Store for display if needed
        if commit:
            driver.save()
        return driver
