from django import forms
from django.contrib.auth.forms import SetPasswordForm

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
    )
    new_password2 = forms.CharField(
        label="Confirm password",
    )
