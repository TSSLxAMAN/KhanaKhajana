from django import forms
from .models import Cuisine

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