from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

from .forms import SignupForm
from .models import CustomerProfile, SellerProfile


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()

    return render(
        request,
        'registration/signup.html',
        {'form': form}
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(
        request,
        'registration/login.html',
        {'form': form}
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')



@login_required
def customer_panel(request):
    customer = CustomerProfile.objects.filter(
        user=request.user
    ).first()

    if customer is None:
        if SellerProfile.objects.filter(user=request.user).exists():
            return redirect('seller_panel')
        return redirect('home')

    return render(
        request,
        'customer_panel.html',
        {'customer': customer}
    )



@login_required
def payment_view(request):
    customer = CustomerProfile.objects.filter(
        user=request.user
    ).first()

    if customer is None:
        return redirect('seller_panel')

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except (InvalidOperation, TypeError):
            amount = Decimal('0')

        if amount.is_finite() and amount > 0:
            customer.balance += amount
            customer.save(update_fields=['balance'])
            messages.success(request, 'Balance updated successfully.')
            return redirect('customer_panel')

    return render(
        request,
        'payment.html',
        {'customer': customer}
    )