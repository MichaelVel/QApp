from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import EmailInput, PasswordInput, TextInput


# Create your forms here.

class NewUserForm(UserCreationForm):
    password1 = forms.CharField(label="Password",
            strip=False,
            widget=forms.PasswordInput(attrs={
                "class": "form-control",
                "autocomplete": "new-password"}))

    password2 = forms.CharField(label="Password Confirmation",
            strip=False,
            widget=forms.PasswordInput(attrs={
                "class": "form-control",
                "autocomplete": "new-password"}))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = { 
                'username': TextInput(attrs={
                    'class': "form-control",
                    }),
                'email': EmailInput(attrs={
                    'class': "form-control",
                    }),
        }

    
    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

