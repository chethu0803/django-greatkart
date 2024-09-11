from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from cart.models import Cart,CartItems
from cart.views import _cart_id
from django.db.models import Q
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
# Create your views here.
def store(request,category_slug=None):
  try:
    if category_slug:
      category_obj=get_object_or_404(Category,slug=category_slug)
      products=Product.objects.filter(category=category_obj, is_available=True).order_by('id')
      paginator=Paginator(products,2)
      page=request.GET.get('page',1)
      paged_products=paginator.get_page(page)
    else:
      products=Product.objects.all().filter(is_available=True).order_by('id')
      paginator=Paginator(products,2)
      page=request.GET.get('page',1)
      paged_products=paginator.get_page(page)
    products_count=products.count()
  except PageNotAnInteger:
        page_obj = paginator.get_page(1)  # If page is not an integer, show the first page
  except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages) 
  return render(request,'store.html',{'products':paged_products,'products_count':products_count,})

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

def search(request):
  if 'keyword' in request.GET:
    keyword=request.GET['keyword']
    products=Product.objects.order_by('-created_date').filter(Q(product_name__icontains=keyword) | Q(description__icontains=keyword))
  products_count=products.count()
  context={
    'products':products,
    'products_count':products_count,
  }
  return render(request,'store.html',context)