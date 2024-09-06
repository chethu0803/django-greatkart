from django.db import models
from category.models import Category
# Create your models here.
class Product(models.Model):
  product_name=models.CharField(max_length=200,unique=True)
  slug=models.SlugField(max_length=200,unique=True)
  price=models.IntegerField()
  description=models.TextField(max_length=400,blank=True)
  images=models.ImageField(upload_to='photos/products')
  stock=models.IntegerField()
  is_available=models.BooleanField(default=True)
  created_date=models.DateTimeField(auto_now_add=True)
  modified_date=models.DateTimeField(auto_now=True)
  category=models.ForeignKey(Category,on_delete=models.CASCADE)

  def __str__(self):
    return self.product_name
