from django import forms
from .models import Product, Review, Order, ProductVariant

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'brand', 'description', 'default_price', 'photo']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'default_price': forms.NumberInput(attrs={'step': 0.01}),
        }

        def clean_default_price(self):
            price = self.cleaned_data['default_price']
            if price <= 0:
                raise forms.ValidationError("Цена должна быть положительной")
            return price
        
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['product', 'rating', 'name', 'description']
        
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address', 'full_price']


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'product', 'color', 'price', 'description']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'step': 0.01}),
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Цена должна быть положительной")
        return price