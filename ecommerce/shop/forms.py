from django import forms
from .models import Category, Brand

class ProductFilterForm(forms.Form):
    PRICE_CHOICES = [
        ('', 'All Prices'),
        ('0-50', 'Under $50'),
        ('50-100', '$50 - $100'),
        ('100-200', '$100 - $200'),
        ('200-500', '$200 - $500'),
        ('500+', 'Over $500'),
    ]
    
    SORT_CHOICES = [
        ('', 'Default'),
        ('price', 'Price: Low to High'),
        ('-price', 'Price: High to Low'),
        ('name', 'Name: A to Z'),
        ('-name', 'Name: Z to A'),
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
    ]
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        empty_label='All Brands',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    price_range = forms.ChoiceField(
        choices=PRICE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    featured_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    available_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )