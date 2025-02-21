from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Variation
from django.http import HttpResponse
from .models import Cart,CartItems
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


# Create your views here.
def _cart_id(request):
  if request.session.session_key:
    return request.session.session_key
  else:
    return request.session.create()


def add_cart(request,product_id):
  product=get_object_or_404(Product,id=product_id)
  current_user=request.user
  if current_user.is_authenticated:
    if product.stock>0:      
      try:
        if request.method=="POST":
          product_variation=[]
          for item in request.POST:
            key=item
            value=request.POST[key]

            try:
              variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
              product_variation.append(variation)
            except:
              pass
          
          is_cart_items=CartItems.objects.filter(product=product,user=current_user).exists()

          if is_cart_items:
            cart_items=CartItems.objects.filter(product=product,user=current_user)
            ex_var_list=[]
            id=[]

            for item in cart_items:
              existing_variation=item.variations.all()
              ex_var_list.append(list(existing_variation))
              id.append(item.id)
            
            
            if product_variation in ex_var_list:
              index=ex_var_list.index(product_variation)    
              item_id=id[index]
              item=CartItems.objects.get(product=product,id=item_id,user=current_user)
              item.quantity+=1
              item.save()
            else:
              item=CartItems.objects.create(product=product,quantity=1,user=current_user)
              if len(product_variation)>0:
                item.variations.clear()
                item.variations.add(*product_variation)
              item.save()

          else:
            cart_item=CartItems.objects.create(
              product=product,quantity=1,user=current_user
            )
            if len(product_variation)>0:
              cart_item.variations.clear()
              cart_item.variations.add(*product_variation)
            cart_item.save()
      except:
        pass
      return redirect('cart')
    
  else:
    if product.stock>0:
      try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
      except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=_cart_id(request))

      try:
        if request.method=="POST":
          product_variation=[]
          for item in request.POST:
            key=item
            value=request.POST[key]

            try:
              variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
              product_variation.append(variation)
            except:
              pass
          
          is_cart_items=CartItems.objects.filter(product=product,cart=cart).exists()
          if is_cart_items:
            cart_item=CartItems.objects.filter(product=product,cart=cart)
            ex_var_list=[]
            id=[]
            for item in cart_item:
              existing_variation=item.variations.all()
              ex_var_list.append(list(existing_variation))
              id.append(item.id)
            
            if product_variation in ex_var_list:
              index=ex_var_list.index(product_variation)
              item_id=id[index]
              item=CartItems.objects.get(product=product,id=item_id,cart=cart)
              item.quantity+=1
              item.save()
            else:
              item=CartItems.objects.create(product=product,quantity=1,cart=cart)
              if len(product_variation)>0:
                item.variations.clear()
                item.variations.add(*product_variation)
              item.save()

          else:
            cart_item=CartItems.objects.create(
              product=product,quantity=1,cart=cart
            )
            if len(product_variation)>0:
              cart_item.variations.clear()
              cart_item.variations.add(*product_variation)
            cart_item.save()
      except:
        pass
      return redirect('cart')
  
  return render(request,'product.html',{'product':product})


def cart(request,total=0,quantity=0,tax=0,cart_items=None,grand_total=0):
  if request.user.is_authenticated:
    try:
      cart_items=CartItems.objects.filter(user=request.user,is_active=True)
      for item in cart_items:
        total+=(item.product.price*item.quantity)
        quantity+=item.quantity
      tax=(2*total)/100
      grand_total=total+tax
    except CartItems.DoesNotExist:
      pass
    context={
      'total':total,
      'quantity':quantity,
      'cart_items':cart_items,
      'tax':tax,
      'grand_total':grand_total
    }
  else:
    try:
      cart=Cart.objects.get(cart_id=_cart_id(request))
      cart_items=CartItems.objects.filter(cart=cart,is_active=True)
      for item in cart_items:
        total+=(item.product.price*item.quantity)
        quantity+=item.quantity
      tax=(2*total)/100
      grand_total=total+tax
    except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=_cart_id(request))
    
    context={
      'total':total,
      'quantity':quantity,
      'cart_items':cart_items,
      'tax':tax,
      'grand_total':grand_total
    }
  return render(request,'cart.html',context)


def remove(request,product_id,cart_item_id):
  product=get_object_or_404(Product,id=product_id)
  if request.user.is_authenticated:
    cart_items=CartItems.objects.get(user=request.user,product=product)
  else:
    cart=Cart.objects.get(cart_id=_cart_id(request))
    cart_items=CartItems.objects.get(cart=cart,product=product,is_active=True,id=cart_item_id)
  if cart_items.quantity>1:
    cart_items.quantity-=1
    cart_items.save()
  else:
    cart_items.delete()
  
  return redirect("cart")
  

def remove_item(request,product_id,cart_item_id):
  product=Product.objects.get(id=product_id)
  if request.user.is_authenticated:
    cart_item=CartItems.objects.get(user=request.user,product=product,is_active=True,id=cart_item_id)
  else:
    cart=Cart.objects.get(cart_id=_cart_id(request))
    cart_item=CartItems.objects.get(cart=cart,product=product,is_active=True,id=cart_item_id)
  cart_item.delete()
  return redirect("cart")

@login_required(login_url='login')
def checkout(request,tax=0,grand_total=0,total=0,quantity=0):
  if request.user.is_authenticated:
    try:
      cart_items=CartItems.objects.filter(user=request.user,is_active=True)
      for item in cart_items:
        total+=(item.product.price*item.quantity)
        quantity+=item.quantity
      tax=(2*total)/100
      grand_total=total+tax
    except :
        pass
    context={
      'total':total,
      'quantity':quantity,
      'cart_items':cart_items,
      'tax':tax,
      'grand_total':grand_total
    }
  else:
    try:
      cart=Cart.objects.get(cart_id=_cart_id(request))
      cart_items=CartItems.objects.filter(cart=cart,is_active=True)
      for item in cart_items:
        total+=(item.product.price*item.quantity)
        quantity+=item.quantity
      tax=(2*total)/100
      grand_total=total+tax
    except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=_cart_id(request))
    
    context={
      'total':total,
      'quantity':quantity,
      'cart_items':cart_items,
      'tax':tax,
      'grand_total':grand_total
    }
  return render(request,'checkout.html',context)