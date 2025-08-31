from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import F
from .models import Cart, CartItem
from shop.models import Product
import json

def get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart

def cart_detail(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all()
    }
    return render(request, 'cart/cart_detail.html', context)

@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    
    # Check if product is available
    if not product.available or product.stock < quantity:
        messages.error(request, f'Sorry, {product.name} is not available in the requested quantity.')
        return redirect('shop:product_detail', slug=product.slug)
    
    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # Update quantity if item already exists
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, f'Cannot add more items. Only {product.stock} items available.')
            return redirect('shop:product_detail', slug=product.slug)
        cart_item.quantity = new_quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart successfully!')
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart successfully!',
            'cart_total_items': cart.total_items,
            'cart_total_price': float(cart.total_price)
        })
    
    return redirect('cart:cart_detail')

@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        
        if quantity > cart_item.product.stock:
            messages.error(request, f'Cannot update quantity. Only {cart_item.product.stock} items available.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
    
    except ValueError:
        messages.error(request, 'Please enter a valid quantity.')
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_total': float(cart_item.total_price),
            'cart_total_items': cart.total_items,
            'cart_total_price': float(cart.total_price)
        })
    
    return redirect('cart:cart_detail')

@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f'{product_name} removed from cart.')
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from cart.',
            'cart_total_items': cart.total_items,
            'cart_total_price': float(cart.total_price)
        })
    
    return redirect('cart:cart_detail')

@require_POST
def clear_cart(request):
    """Clear all items from cart"""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'Cart cleared successfully!')
    return redirect('cart:cart_detail')

def get_cart_count(request):
    """Get cart item count for AJAX requests"""
    cart = get_or_create_cart(request)
    return JsonResponse({
        'cart_count': cart.total_items,
        'cart_total': float(cart.total_price)
    })