from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import CustomerProfile
from stores.models import Product, Store
from .models import CartItem, Order, OrderItem


@login_required
@require_POST
def add_to_cart(request, product_id):
    customer = getattr(request.user, 'customerprofile', None)

    if customer is None:
        messages.error(request, 'Only customer accounts can buy products.')
        return redirect('home')

    product = get_object_or_404(Product, pk=product_id)

    item, created = CartItem.objects.get_or_create(
        customer=customer,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        item.quantity += 1
        item.save(update_fields=['quantity'])

    return redirect('cart')


@login_required
def cart_view(request):
    customer = getattr(request.user, 'customerprofile', None)

    if customer is None:
        messages.error(request, 'Only customer accounts have a cart.')
        return redirect('home')

    cart_items = CartItem.objects.filter(
        customer=customer
    ).select_related('product', 'product__store')

    total = sum(
        (item.product.price * item.quantity for item in cart_items),
        Decimal('0.00')
    )

    return render(
        request,
        'cart.html',
        {'cart_items': cart_items, 'total': total}
    )


@login_required
@require_POST
def remove_from_cart(request, item_id):
    customer = getattr(request.user, 'customerprofile', None)

    if customer is None:
        return redirect('home')

    item = get_object_or_404(
        CartItem,
        pk=item_id,
        customer=customer
    )
    item.delete()
    return redirect('cart')


@login_required
@require_POST
def update_cart_item(request, item_id):
    customer = getattr(request.user, 'customerprofile', None)

    if customer is None:
        return redirect('home')

    item = get_object_or_404(
        CartItem,
        pk=item_id,
        customer=customer
    )

    action = request.POST.get('action')

    if action == 'increase':
        item.quantity += 1
        item.save(update_fields=['quantity'])
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
        item.save(update_fields=['quantity'])

    return redirect('cart')


@login_required
@require_POST
def checkout(request):
    with transaction.atomic():
        customer = CustomerProfile.objects.select_for_update().filter(
            user=request.user
        ).first()

        if customer is None:
            messages.error(request, 'Customer profile not found.')
            return redirect('cart')

        cart_items = list(
            CartItem.objects.select_for_update(of=('self',))
            .filter(customer=customer)
            .select_related('product', 'product__store')
            .order_by('id')
        )

        if not cart_items:
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')

        total = sum(
            (item.product.price * item.quantity for item in cart_items),
            Decimal('0.00')
        )

        if customer.balance < total:
            messages.error(
                request,
                'Insufficient balance. Please increase your balance.'
            )
            return redirect('payment')

        store_ids = sorted({
            item.product.store_id for item in cart_items
        })

        stores = {
            store.pk: store
            for store in Store.objects.select_for_update()
            .filter(pk__in=store_ids)
            .order_by('pk')
        }

        order = Order.objects.create(
            customer=customer,
            total_amount=total
        )

        order_items = []
        store_totals = {
            store_id: Decimal('0.00')
            for store_id in store_ids
        }

        for item in cart_items:
            order_items.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            )

            store_totals[item.product.store_id] += (
                item.product.price * item.quantity
            )

        OrderItem.objects.bulk_create(order_items)

        customer.balance -= total
        customer.save(update_fields=['balance'])

        for store_id, amount in store_totals.items():
            store = stores[store_id]
            store.balance += amount
            store.save(update_fields=['balance'])

        CartItem.objects.filter(
            customer=customer,
            id__in=[item.id for item in cart_items]
        ).delete()

        messages.success(request, 'Order placed successfully!')

    return redirect('order_history')


@login_required
def order_history(request):
    customer = getattr(request.user, 'customerprofile', None)

    if customer is None:
        messages.error(request, 'Only customer accounts have order history.')
        return redirect('home')

    orders = Order.objects.filter(
        customer=customer
    ).order_by('-created_at')

    return render(
        request,
        'order_history.html',
        {'orders': orders}
    )
