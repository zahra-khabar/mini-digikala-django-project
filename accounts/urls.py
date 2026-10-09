from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('customer/', views.customer_panel, name='customer_panel'),
    path('seller/', views.seller_panel, name='seller_panel'),
    path('payment/', views.payment_view, name='payment'),
]