from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from cart.models import Cart,CartItems
from cart.views import _cart_id
# Create your views here.
def store(request,category_slug=None):
  if category_slug:
    category_obj=get_object_or_404(Category,slug=category_slug)
    products=Product.objects.filter(category=category_obj, is_available=True)
  else:
    products=Product.objects.all().filter(is_available=True)
  products_count=products.count()
  return render(request,'store.html',{'products':products,'products_count':products_count})

def product(request,category_slug,product_slug):
  try:
    product=Product.objects.get(slug=product_slug)
    cart=Cart.objects.get(cart_id=_cart_id(request))
    in_cart=CartItems.objects.filter(cart=cart,product=product).exists()
  except Exception as e:
    raise e
  context={
    'product':product,
    'in_cart':in_cart,
    }
  return render(request,'product.html',context)