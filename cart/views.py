from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product
from django.http import HttpResponse
from .models import Cart,CartItems
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
def _cart_id(request):
  try:
    cart_id=request.session.session_key
  except:
    cart_id=request.session.create()
  return cart_id


def add_cart(request,product_id):
  product=get_object_or_404(Product,id=product_id)
  try:
    cart=Cart.objects.get(cart_id=_cart_id(request))
  except Cart.DoesNotExist:
    cart=Cart.objects.create(cart_id=_cart_id(request))

  try:
    cart_items=CartItems.objects.get(product=product,cart=cart)
    cart_items.quantity+=1
    cart_items.save()
  except CartItems.DoesNotExist:
    cart_items=CartItems.objects.create(product=product,cart=cart,quantity=1)
  
  return redirect('cart')


def cart(request,total=0,quantity=0,cart_items=None):
  try:
    cart=Cart.objects.get(cart_id=_cart_id(request))
    cart_items=CartItems.objects.filter(cart=cart,is_active=True)
    for item in cart_items:
      total+=(item.product.price*item.quantity)
      quantity+=item.quantity
    tax=(2*total)/100
    grand_total=total+tax
  except ObjectDoesNotExist:
    pass
  
  context={
    'total':total,
    'quantity':quantity,
    'cart_items':cart_items,
    'tax':tax,
    'grand_total':grand_total
  }
  return render(request,'cart.html',context)


def remove(request,product_id):
  product=get_object_or_404(Product,id=product_id)
  cart=Cart.objects.get(cart_id=_cart_id(request))
  cart_items=CartItems.objects.get(cart=cart,product=product,is_active=True)
  if cart_items.quantity>1:
    cart_items.quantity-=1
    cart_items.save()
  else:
    cart_items.delete()
  
  return redirect("cart")
  

def remove_item(request,product_id):
  product=Product.objects.get(id=product_id)
  cart=Cart.objects.get(cart_id=_cart_id(request))
  cart_item=CartItems.objects.get(cart=cart,product=product,is_active=True)
  cart_item.delete()
  return redirect("cart")