from django.shortcuts import render
from django.shortcuts import HttpResponse,render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required

#Email Verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
# Create your views here.
def register(request):
  if request.method=="POST":
    form=RegistrationForm(request.POST)
    if form.is_valid(): #is_valid() validates all fields by default rules like email should contain '@',etc.It also invokes clean() from formClass.Two Things:Validation and Cleaning(trim white space,etc)
      first_name=form.cleaned_data['first_name']
      last_name=form.cleaned_data['last_name']
      email=form.cleaned_data['email']
      phone_num=form.cleaned_data['phone_number']
      password=form.cleaned_data['first_name']
      username=email.split('@')[0]
      user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,password=password,username=username)
      user.phone_number=phone_num
      user.save()
      messages.success(request,"Registration Successful.")
      
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
  if request.method=="POST":
    email=request.POST['email']
    password=request.POST['password']

    user=auth.authenticate(email=email,password=password)
    if user is not None:
      auth.login(request,user)
      return redirect("dashboard")
    else:
      messages.error(request,"Invalid Login Credentials")
  return render(request,'login.html')

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
  return render(request,'dashboard.html')

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



