from django.shortcuts import render
from django.shortcuts import HttpResponse,render,redirect
from .forms import RegistrationForm
from .models import Account,UserProfile
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from cart.models import Cart,CartItems
from cart.views import _cart_id
from .forms import UserProfileForm,UserForm
import requests
from order.models import Order,OrderProduct
from django.db.models import Count
#Email Verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import cloudinary
import cloudinary.api
# Create your views here.
def register(request):
  if request.method=="POST":
    form=RegistrationForm(request.POST)
    if form.is_valid(): #is_valid() validates all fields by default rules like email should contain '@',etc.It also invokes clean() from formClass.Two Things:Validation and Cleaning(trim white space,etc)
      first_name=form.cleaned_data['first_name']
      last_name=form.cleaned_data['last_name']
      email=form.cleaned_data['email']
      phone_num=form.cleaned_data['phone_number']
      password=form.cleaned_data['password']
      username=email.split('@')[0]
      user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,password=password,username=username)
      user.phone_number=phone_num
      user.save()
      messages.success(request,"Registration Successful.")

      profile=UserProfile()
      profile.user_id=user.id
      default_pic=cloudinary.api.resource_by_asset_id("39deff3aa17393db3ed4cdde26ef428f")
      profile.profile_picture=default_pic['secure_url']
      profile.save()
      
      #Email Verification
      current_site=get_current_site(request)
      mail_subject='Please Activate your Account.'
      message=render_to_string('activation_email.html',{
        'user':user,
        'domain':current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':default_token_generator.make_token(user)
      })
      to_email=email
      send_email=EmailMessage(mail_subject,message,to=[to_email])
      send_email.send()
      return redirect('/account/login/?command=verification&email='+email)
    else:
      messages.error(request,"Password does not match")
  else:    
    form=RegistrationForm()
  context={
    'form':form,
  }
  return render(request,'register.html',context)

def login(request):
  if request.method == 'POST':
    email = request.POST['email']
    password = request.POST['password']

    user = auth.authenticate(email=email, password=password)

    if user is not None:
      try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        is_cart_item_exists = CartItems.objects.filter(cart=cart).exists()
        if is_cart_item_exists:
          cart_item = CartItems.objects.filter(cart=cart)

          # Getting the product variations by cart id
          product_variation = []
          for item in cart_item:
            variation = item.variations.all()
            product_variation.append(list(variation))

          # Get the cart items from the user to access his product variations
          cart_item = CartItems.objects.filter(user=user)
          ex_var_list = []
          id = []
          for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

          for pr in product_variation:
            if pr in ex_var_list:
              index = ex_var_list.index(pr)
              item_id = id[index]
              item = CartItems.objects.get(id=item_id)
              item.quantity += 1
              item.user = user
              item.save()
            else:
              cart_item = CartItems.objects.filter(cart=cart)
              for item in cart_item:
                item.user = user
                item.save()
      except:
        pass
      auth.login(request, user)
      url=request.META.get("HTTP_REFERER")
      try:
        query=requests.utils.urlparse(url).query
        params=dict(x.split('=') for x in query.split('&'))
        if 'next' in params:
          nextPage=params['next']
          return redirect(nextPage)
      except:
        return redirect('dashboard')
    else:
      messages.error(request, 'Invalid login credentials')
      return redirect('login')
    
  return render(request, 'login.html')

@login_required(login_url='login')
def logout(request):
  auth.logout(request)
  messages.success(request,"You are logged out")
  return redirect("login")

def activate(request,uidb64,token):
  try:
    uid=urlsafe_base64_decode(uidb64).decode()
    user=Account._default_manager.get(pk=uid)
  except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
    user=None
  
  if user is not None and default_token_generator.check_token(user,token):
    user.is_active=True
    user.save()
    messages.success(request,"Congratulations, Your Account is Activated.")
    return redirect('login')
  else:
    messages.error(request,'Invalid Activation Link')
    return redirect('register')
  
@login_required(login_url='login')
def dashboard(request):
  user_profile=UserProfile.objects.get(user_id=request.user.id)
  count=Order.objects.filter(user_id=request.user.id,is_ordered=True).aggregate(count=Count('id'))
  orders_count=count['count']
  context={
    'user_profile':user_profile,
    'orders_count':orders_count
  }
  return render(request,'dashboard.html',context)

@login_required(login_url='login')
def forgotPassword(request):
  if request.method=="POST":
    email=request.POST['email']
    
    if Account.objects.filter(email=email).exists():
      user=Account.objects.get(email__exact=email)

      #Reset password mail
      current_site=get_current_site(request)
      mail_subject='Reset Your Password.'
      message=render_to_string('resetPassword_email.html',{
        'user':user,
        'domain':current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':default_token_generator.make_token(user)
      })
      to_email=email
      send_email=EmailMessage(mail_subject,message,to=[to_email])
      send_email.send()
      messages.success(request,"Password reset email has been sent to your email address.")
      return redirect('login')
    else:
      messages.error(request,'Account does not exist')
      return redirect('register')
  return render(request,'forgotPassword.html')

@login_required(login_url='login')
def resetPassword_validate(request,uidb64,token):
  try:
    uid=urlsafe_base64_decode(uidb64).decode()
    user=Account._default_manager.get(pk=uid)
  except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
    user=None
  
  if user is not None and default_token_generator.check_token(user,token):
    request.session['uid']=uid
    messages.success(request,'Please reset your Password.')
    return redirect('resetPassword')
  else:
    messages.error(request,'The link has been expired.')
    return redirect('forgotPassword')
  
def resetPassword(request):
  if request.method=="POST":
    password=request.POST['password']
    confirm_password=request.POST['confirm_password']

    if password==confirm_password:
      uid=request.session.get('uid')
      user=Account.objects.get(pk=uid)
      user.set_password(password)
      user.save()
      messages.success(request,'Password reset seccessful.')
      return redirect('login')
    else:
      messages.error(request,"Password do no match.")
      return redirect('resetPassword')
  return render(request,'resetPassword.html')

@login_required(login_url='login')
def my_orders(request):
  orders=Order.objects.order_by('-created_at').filter(user=request.user,is_ordered=True)
  context={
    'orders':orders
  }
  return render(request,'my_orders.html',context)

@login_required(login_url='login')
def edit_profile(request):
  try:
    userprofile=UserProfile.objects.get(user_id=request.user.id)
  except:
    pass
  if request.method=="POST":
    user_form=UserForm(request.POST,instance=request.user)
    profile_form=UserProfileForm(request.POST,request.FILES,instance=userprofile)
    if user_form.is_valid() and profile_form.is_valid():
      user_form.save()
      if profile_form.cleaned_data['profile_pic']:
        userprofile.profile_picture=profile_form.cleaned_data['profile_pic']
      profile_form.save()
      userprofile.save()
      messages.success(request,'Your Profile has been Updated.')
      return redirect('edit_profile')
  else:
    user_form=UserForm(instance=request.user)
    profile_form=UserProfileForm(instance=userprofile)
    context={
      'user_form':user_form,
      'profile_form':profile_form,
      'userProfile':userprofile,
    }
  return render(request,'edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method=="POST":
      current_password=request.POST['current_password']
      new_password=request.POST['new_password']
      confirm_password=request.POST['confirm_password']
      
      user=Account.objects.get(username__exact=request.user.username)

      if user.check_password(current_password):
        if new_password==confirm_password:
          user.set_password(new_password)
          user.save()
          messages.success(request,"Password updated successfully.")
          return redirect('change_password')
        else:
          messages.error(request,'Password does not match!')
          return redirect('change_password')
      else:
          messages.error(request,'Please enter valid current Password')
          return redirect('change_password')
    return render(request,'change_password.html')

@login_required(login_url='login')
def order_detail(request,order_id):
  order=Order.objects.get(order_number=order_id)
  orderproducts=OrderProduct.objects.filter(user=request.user,order=order)

  sub_total=order.order_total-order.tax
  context={
    'order':order,
    'sub_total':sub_total,
    'orderproducts':orderproducts,
  }
  return render(request,'order_detail.html',context)









