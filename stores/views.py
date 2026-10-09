from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Store,Product
from .forms import StoreForm, ProductForm
from accounts.models import SellerProfile

def stores_list(request):
    """Lists of All Stores From DB"""
    stores = Store.objects.all()
    return render(request,'stores/stores.html',{'stores':stores})

def store_detail(request,store_id):
    """Details of custom store with their products"""
    store = get_object_or_404(Store,id=store_id)
    products = store.products.all()

    #check that user is owner of our store or Not!
    is_owner = False
    if request.user.is_authenticated:
        try:
            seller_profile = SellerProfile.user.sellerprofile
            if store.owner == seller_profile:
                is_owner = True
        except SellerProfile.DoesNotExist:
            pass
    return render(request,'stores/store_detail.html',{'store':store,'products':products,'is_owner':is_owner})

@login_required
def create_store(request):
    """Creates new store For Sellers"""
    try:
        seller_profile = SellerProfile.user.sellerprofile

    except SellerProfile.DoesNotExist:
        return HttpResponseForbidden("You are not allowed to create store as Seller, You must login before")

    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = seller_profile
            form.save()
            return redirect('store_detail', store_id=store.id)
    else:
        form = StoreForm()

    return render(request,'stores/create_store.html', {'form': form})

@login_required
def add_product(request,store_id):
    """Adds product to store with store id . only sellers can do that!"""
    store = get_object_or_404(Store,id=store_id)

    try:
        seller_profile = SellerProfile.user.sellerprofile
        if store.owner != seller_profile:
            return HttpResponseForbidden("You are not allowed to create store")
    except SellerProfile.DoesNotExist:
        return HttpResponseForbidden("You are not a seller.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = seller_profile
            product.save()
            return redirect('store_detail', store_id=store.id)
    else:
        form = ProductForm()

    return render(request, 'stores/add_product.html', {'form': form, 'store': store})

@login_required
def seller_panel(request):
    """Seller Panel - Show them Stores"""
    try:
        seller_profile = SellerProfile.user.sellerprofile
    except SellerProfile.DoesNotExist:
        return HttpResponseForbidden("You are not a seller!")
    stores = seller_profile.stores.all()
    return render(request,'stores/seller_panel.html', {'stores': stores})



