from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path(
        'remove/<int:item_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),
    path('history/', views.order_history, name='order_history'),
]