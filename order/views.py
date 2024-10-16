from django.shortcuts import render,redirect,HttpResponse
from cart.models import CartItems
from .forms import OrderForm
from .models import Order,Payment,OrderProduct,Product
import datetime
import razorpay
from greatkart.settings import RAZOR_PAY_ID,RAZOR_PAY_KEY
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
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
      data.last_name=form.cleaned_data['last_name']
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

      client = razorpay.Client(auth=(RAZOR_PAY_ID, RAZOR_PAY_KEY))
      data={
        'amount':int(grand_total*100),
        'currency':'INR'
      }
      payment_order=client.order.create(data=data)
      order_id=payment_order['id']
      if payment_order['id']:
        payment=Payment()
        payment.user=request.user
        payment.razorpay_order_id=payment_order['id']
        payment.status=payment_order['status']
        payment.save()
        order.payment=payment
        order.save()
      
      context={
        'order':order,
        'tax':tax,
        'grand_total':grand_total,
        'total':total,
        'cart_items':cart_items,
        'payment':payment,
        'key':RAZOR_PAY_ID,
        'order_id':order_id,
      }
      return render(request,'payments.html',context)
  else:
    return redirect('checkout')
  
@csrf_exempt
def payment_successfull(request):
  if request.method=="POST":

    payment=Payment.objects.get(razorpay_order_id=request.POST['razorpay_order_id'])
    payment.razorpay_payment_id=request.POST['razorpay_payment_id']
    payment.razorpay_signature=request.POST['razorpay_signature']

    client = razorpay.Client(auth=(RAZOR_PAY_ID, RAZOR_PAY_KEY))
    payment_order_id=payment.razorpay_order_id

    try:
      client.utility.verify_payment_signature({
                'razorpay_order_id': payment_order_id,
                'razorpay_payment_id': payment.razorpay_payment_id,
                'razorpay_signature': payment.razorpay_signature,
            })
    except:
      return HttpResponse("Payment verification failed", status=400)
    
    payment_details = client.payment.fetch(request.POST['razorpay_payment_id'])
    payment_method = payment_details.get('method')
    order=Order.objects.get(payment=payment)
    order.is_ordered=True
    order.status="Completed"
    payment.amount_paid=order.order_total
    payment.status='Completed'
    payment.payment_method=payment_method
    payment.save()
    
    order.save()
    sub_total=order.order_total-order.tax
    
    #Move the items to OrderProduct 
    cart_items=CartItems.objects.filter(user=request.user)
    for item in cart_items:
      orderproduct=OrderProduct()
      orderproduct.order=order
      orderproduct.payment=payment
      orderproduct.user=request.user
      orderproduct.quantity=item.quantity
      orderproduct.product_price=item.product.price
      orderproduct.product=item.product
      orderproduct.ordered=True
      orderproduct.save()

      product_variation=item.variations.all()
      orderproduct.variations.set(product_variation)
      orderproduct.save()
    

      product=Product.objects.get(id=item.product.id)
      product.stock-=item.quantity
      product.save()

    CartItems.objects.filter(user=request.user).delete()

    mail_subject="Thank You for your order!"
    message=render_to_string('order_received_email.html',{
      'user':request.user,
      'transID':request.POST['razorpay_payment_id'],
      'order':order,
    })
    to_email=request.user.email
    send_email=EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()
    orderproducts=OrderProduct.objects.filter(user=request.user,payment=payment)
    payment=True
    context={
      'order':order,
      'sub_total':sub_total,
      'payment':payment,
      'orderproducts':orderproducts
    }
    return render(request,'order_detail.html',context)
    
  
