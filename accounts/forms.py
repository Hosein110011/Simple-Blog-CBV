from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile


class UserRegistrationForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    password1 = forms.CharField(label='password' ,widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label='confirm password' ,widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def clean_email(self):
        email = self.cleaned_data["email"]
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError('this email alreaddy exists!')
        return email
    
    def clean_data(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError('password must match')
        

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))


class EditUserForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = Profile
        fields = ['age', 'bio']
