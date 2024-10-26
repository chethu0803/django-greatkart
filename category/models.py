from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.
class Category(models.Model):
  category_name=models.CharField(max_length=50,unique=True)
  slug=models.SlugField(max_length=100,unique=True)
  description=models.TextField(max_length=200,blank=True)
  cat_image=CloudinaryField('image', folder='admin_uploads/Category',tags='Category')

  class Meta:
    verbose_name='category'
    verbose_name_plural='categories'

  def __str__(self):
    return self.category_name