from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('cart/success/<int:order_id>/', views.checkout_success, name='checkout_success'),
    path('orders/', views.order_history, name='order_history'),
]
