from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductForm, StoreForm
from .models import Product, Store


def stores_list(request):
    stores = Store.objects.all()

    return render(
        request,
        'stores/stores.html',
        {'stores': stores}
    )


def store_detail(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    products = store.products.all()

    seller = getattr(request.user, 'sellerprofile', None)
    is_owner = seller is not None and store.owner_id == seller.pk

    return render(
        request,
        'stores/store_detail.html',
        {'store': store, 'products': products, 'is_owner': is_owner}
    )


@login_required
def create_store(request):
    seller = getattr(request.user, 'sellerprofile', None)

    if seller is None:
        messages.error(
            request,
            'فقط حساب‌های فروشنده می‌توانند فروشگاه بسازند.'
        )
        return redirect('customer_panel')

    if request.method == 'POST':
        form = StoreForm(request.POST)

        if form.is_valid():
            store = form.save(commit=False)
            store.owner = seller
            store.save()
            return redirect('store_detail', store_id=store.pk)
    else:
        form = StoreForm()

    return render(
        request,
        'stores/create_store.html',
        {'form': form}
    )


@login_required
def edit_store(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    seller = getattr(request.user, 'sellerprofile', None)

    if seller is None or store.owner_id != seller.pk:
        return HttpResponseForbidden(
            'فقط می‌توانید فروشگاه‌های خودتان را ویرایش کنید.'
        )

    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)

        if form.is_valid():
            form.save()
            messages.success(request, 'فروشگاه به‌روزرسانی شد.')
            return redirect('store_detail', store_id=store.pk)
    else:
        form = StoreForm(instance=store)

    return render(
        request,
        'stores/edit_store.html',
        {'form': form, 'store': store}
    )


@login_required
def add_product(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    seller = getattr(request.user, 'sellerprofile', None)

    if seller is None or store.owner_id != seller.pk:
        return HttpResponseForbidden(
            'فقط می‌توانید محصولات فروشگاه‌های خودتان را مدیریت کنید.'
        )

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect('store_detail', store_id=store.pk)
    else:
        form = ProductForm()

    return render(
        request,
        'stores/add_product.html',
        {'form': form, 'store': store}
    )


@login_required
def edit_product(request, store_id, product_id):
    store = get_object_or_404(Store, pk=store_id)
    product = get_object_or_404(Product, pk=product_id, store=store)
    seller = getattr(request.user, 'sellerprofile', None)

    if seller is None or store.owner_id != seller.pk:
        return HttpResponseForbidden(
            'فقط می‌توانید محصولات فروشگاه‌های خودتان را مدیریت کنید.'
        )

    if request.method == 'POST':
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():
            form.save()
            return redirect('store_detail', store_id=store.pk)
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        'stores/edit_product.html',
        {'form': form, 'store': store, 'product': product}
    )


@login_required
@require_POST
def delete_product(request, store_id, product_id):
    store = get_object_or_404(Store, pk=store_id)
    product = get_object_or_404(Product, pk=product_id, store=store)
    seller = getattr(request.user, 'sellerprofile', None)

    if seller is None or store.owner_id != seller.pk:
        return HttpResponseForbidden(
            'فقط می‌توانید محصولات فروشگاه‌های خودتان را مدیریت کنید.'
        )

    try:
        product.delete()
    except ProtectedError:
        messages.error(
            request,
            'این محصول سفارش ثبت‌شده دارد و قابل حذف نیست.'
        )
        return redirect('store_detail', store_id=store.pk)

    messages.success(request, 'محصول حذف شد.')

    return redirect('store_detail', store_id=store.pk)


@login_required
def seller_panel(request):
    seller = getattr(request.user, 'sellerprofile', None)

    if seller is None:
        messages.error(
            request,
            'پنل فروشنده فقط برای حساب‌های فروشنده است.'
        )
        return redirect('customer_panel')

    stores = seller.stores.all()

    return render(
        request,
        'stores/seller_panel.html',
        {'stores': stores}
    )
