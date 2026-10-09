from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import CartItem, Order


@login_required
def cart_view(request):
    cart_items = list(
        CartItem.objects.filter(
            customer=request.user
        ).select_related('product', 'product__store')
    )

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return render(
        request,
        'cart.html',
        {
            'cart_items': cart_items,
            'total': total,
        }
    )


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        customer=request.user
    )

    item.delete()
    return redirect('cart')


@login_required
def order_history(request):
    orders = Order.objects.filter(
        customer=request.user
    ).order_by('-created_at')

    return render(
        request,
        'order_history.html',
        {'orders': orders}
    )