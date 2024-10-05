from django.shortcuts import render,redirect,HttpResponse
from cart.models import CartItems
from .forms import OrderForm
from .models import Order
import datetime
# Create your views here.
def placeorder(request):
  current_user=request.user
  cart_items=CartItems.objects.filter(user=current_user,is_active=True)
  cart_items_count=cart_items.count()

  tax=0
  grand_total=0
  total=0
  quantity=0
  for item in cart_items:
    total+=(item.product.price*item.quantity)
    quantity+=item.quantity
    tax=(2*total)/100
    grand_total=total+tax
  

  if cart_items_count<=0 or current_user==None:
    return redirect('cart')
  
  if request.method=="POST":
    form=OrderForm(request.POST)
    if form.is_valid():
      data=Order()
      data.user=current_user
      data.first_name=form.cleaned_data['first_name']
      data.email=form.cleaned_data['email']
      data.phone=form.cleaned_data['phone']
      data.address_line_1=form.cleaned_data['address_line_1']
      data.address_line_2=form.cleaned_data['address_line_2']
      data.city=form.cleaned_data['city']
      data.state=form.cleaned_data['state']
      data.country=form.cleaned_data['country']
      data.order_note=form.cleaned_data['order_note']
      data.order_total=grand_total
      data.tax=tax
      data.ip=request.META.get("REMOTE_ADDR")
      data.save()

      yr=int(datetime.date.today().strftime("%Y"))
      dt=int(datetime.date.today().strftime("%d"))
      mt=int(datetime.date.today().strftime("%m"))
      d=datetime.date(yr,mt,dt)
      current_date=d.strftime("%Y%m%d")
      order_number=current_date+str(data.id)
      data.order_number=order_number
      data.save()

      order=Order.objects.get(user=current_user,order_number=order_number)

      context={
        'order':order,
        'tax':tax,
        'grand_total':grand_total,
        'total':total,
        'cart_items':cart_items
      }
      return render(request,'payments.html',context)
  else:
    return redirect('checkout')
  
def payments(request):
  return HttpResponse("OK")
  
