from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category, Brand
from .forms import ProductFilterForm

def product_list(request):
    products = Product.objects.all()
    form = ProductFilterForm(request.GET)
    
    # Apply filters
    if form.is_valid():
        # Search filter
        search = form.cleaned_data.get('search')
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search) |
                Q(brand__name__icontains=search)
            )
        
        # Category filter
        category = form.cleaned_data.get('category')
        if category:
            products = products.filter(category=category)
        
        # Brand filter
        brand = form.cleaned_data.get('brand')
        if brand:
            products = products.filter(brand=brand)
        
        # Price range filter
        price_range = form.cleaned_data.get('price_range')
        if price_range:
            if price_range == '0-50':
                products = products.filter(price__lt=50)
            elif price_range == '50-100':
                products = products.filter(price__gte=50, price__lt=100)
            elif price_range == '100-200':
                products = products.filter(price__gte=100, price__lt=200)
            elif price_range == '200-500':
                products = products.filter(price__gte=200, price__lt=500)
            elif price_range == '500+':
                products = products.filter(price__gte=500)
        
        # Featured filter
        featured_only = form.cleaned_data.get('featured_only')
        if featured_only:
            products = products.filter(featured=True)
        
        # Available filter
        available_only = form.cleaned_data.get('available_only')
        if available_only:
            products = products.filter(available=True, stock__gt=0)
        
        # Sort filter
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'form': form,
        'total_products': products.count(),
    }
    
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'shop/product_detail.html', context)

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    
    # Apply pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
    }
    
    return render(request, 'shop/category_products.html', context)
