# core/forms.py
from django import forms
from .models import Profile
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'birth_date', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add fields from the User model
        self.fields['first_name'] = forms.CharField(initial=self.instance.user.first_name)
        self.fields['last_name'] = forms.CharField(initial=self.instance.user.last_name)
        self.fields['email'] = forms.EmailField(initial=self.instance.user.email)  
