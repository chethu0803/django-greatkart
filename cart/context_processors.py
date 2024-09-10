from cart.models import Cart,CartItems
from cart.views import _cart_id

def counter(request):
  cart_count=0
  if 'admin' in request.path:
    return {}
  else:
    try:
      cart=Cart.objects.get(cart_id=_cart_id(request))
      cart_items=CartItems.objects.filter(cart=cart)
      for item in cart_items:
        cart_count+=item.quantity
    except Cart.DoesNotExist:
      cart_count=0
  return dict(cart_count=cart_count)