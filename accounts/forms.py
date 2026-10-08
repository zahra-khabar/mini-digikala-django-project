from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile, SellerProfile


class SignupForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(max_length=20)
    role = forms.ChoiceField(
        choices=[
            ('customer', 'Customer'),
            ('seller', 'Seller'),
        ]
    )

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username already exists.')

        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data

    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        phone = self.cleaned_data['phone']
        role = self.cleaned_data['role']

        user = User.objects.create_user(
            username=username,
            password=password
        )

        if role == 'customer':
            CustomerProfile.objects.create(
                user=user,
                phone=phone
            )
        else:
            SellerProfile.objects.create(
                user=user
            )

        return user