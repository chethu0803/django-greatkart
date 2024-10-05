from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,ReviewRating
from .forms import ReviewForm
from category.models import Category
from cart.models import Cart,CartItems
from cart.views import _cart_id
from django.db.models import Q
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib import messages
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
    product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    in_cart = CartItems.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()
    reviews=ReviewRating.objects.filter(product=product,status=True)
  except Exception as e:
    raise e
  
  context={
    'product':product,
    'in_cart':in_cart,
    'reviews':reviews
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

def submit_review(request,product_id):
   product=Product.objects.get(id=product_id)
   url=request.META.get("HTTP_REFERER")
   if request.user.is_authenticated:
    if request.method=="POST":
        try:
          review =ReviewRating.objects.get(user=request.user,product__id=product_id)
          form=ReviewForm(request.POST,instance=review)
          if form.is_valid():
            form.save()
            messages.success(request,"Thank You! Your review has been updated.")
          return redirect(url)
        except ReviewRating.DoesNotExist:
          form=ReviewForm(request.POST)
          if form.is_valid():
              data=ReviewRating()
              data.rating=form.cleaned_data['rating']
              data.subject=form.cleaned_data['subject']
              data.review=form.cleaned_data['review']
              data.ip=request.META.get("REMOTE_ADDR")
              data.user=request.user
              data.product=product
              data.save()
              messages.success(request,"Thank You! Your Review has been submitted.")
          return redirect(url)
   else:
      return redirect(url)




