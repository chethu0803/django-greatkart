from django.shortcuts import render
from django.shortcuts import HttpResponse,render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages
from django.contrib import auth
# Create your views here.
def register(request):
  if request.method=="POST":
    form=RegistrationForm(request.POST)
    if form.is_valid():
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
      return redirect("register")
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
      return redirect("home")
    else:
      messages.error(request,"Invalid Login Credentials")
  return render(request,'login.html')

def logout(request):
  auth.logout(request)
  messages.success(request,"You are logged out")
  return redirect("login")