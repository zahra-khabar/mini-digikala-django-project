from django.urls import path
from . import views

urlpatterns = [
    path('', views.stores_list, name='stores_list'),
    path('create/', views.create_store, name='create_store'),
    path('seller/panel/', views.seller_panel, name='seller_panel'),
    path('<int:store_id>/', views.store_detail, name='store_detail'),
    path('<int:store_id>/add-product/', views.add_product, name='add_product'),
]