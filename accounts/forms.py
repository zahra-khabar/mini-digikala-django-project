from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomerProfile, SellerProfile


class SignupForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
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
            raise forms.ValidationError(
                'This username already exists.'
            )

        return username

    def clean_password1(self):
        password1 = self.cleaned_data['password1']

        try:
            validate_password(password1)
        except ValidationError as error:
            raise forms.ValidationError(error.messages)

        return password1

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                'Passwords do not match.'
            )

        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )

        role = self.cleaned_data['role']

        if role == 'customer':
            CustomerProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone']
            )
        else:
            SellerProfile.objects.create(
                user=user
            )

        return user