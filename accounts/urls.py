from django.urls import path
from . import views

urlpatterns = [
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('customer/', views.customer_panel, name='customer_panel'),
    path('payment/', views.payment_view, name='payment'),
]
