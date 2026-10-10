from django.urls import path
from . import views

urlpatterns = [
    path('stores/', views.stores_list, name='stores_list'),
    path('stores/create/', views.create_store, name='create_store'),
    path('stores/<int:store_id>/', views.store_detail, name='store_detail'),
    path('stores/<int:store_id>/edit/', views.edit_store, name='edit_store'),
    path('stores/<int:store_id>/add-product/', views.add_product, name='add_product'),
    path('stores/<int:store_id>/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('stores/<int:store_id>/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('seller/', views.seller_panel, name='seller_panel'),
]
