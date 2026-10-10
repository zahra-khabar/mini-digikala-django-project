"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from stores.forms import ProductSearchForm
from stores.models import Product


def home(request):
    search_form = ProductSearchForm(request.GET or None)

    products = Product.objects.select_related(
        'store',
        'category'
    ).order_by('-created_at')

    if search_form.is_bound and search_form.is_valid():
        query = search_form.cleaned_data['q'].strip()
        category = search_form.cleaned_data['category']

        if query:
            products = products.filter(name__icontains=query)

        if category is not None:
            products = products.filter(category=category)

    return render(
        request,
        'home.html',
        {'products': products, 'search_form': search_form}
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('stores.urls')),
    path('', include('orders.urls')),
    path('', home, name='home'),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )