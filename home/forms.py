from django import forms
from django.contrib.auth.forms import SetPasswordForm
from adminapp.models import *
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
    )
    new_password2 = forms.CharField(
        label="Confirm password",
    )

class SetAddressForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address']

class SetMobileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['mobile_number']


