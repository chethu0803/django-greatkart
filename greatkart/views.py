from django.shortcuts import render,HttpResponse
from store.models import Product


def moonhealth(request):
  return HttpResponse("OK",status=200)

def home(request):
  products=Product.objects.all().filter(is_available=True)
  return render(request,'home.html',{'products':products})