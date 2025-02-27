from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from cloudinary.models import CloudinaryField
# Create your models here.
class AccountManager(BaseUserManager):
  def create_user(self,email,first_name,last_name,username,password=None):
    if not email:
      raise ValueError("Enter a Valid email address!!")
    if not username:
      raise ValueError("Enter a valid username!!")
    user=self.model(email=email,first_name=first_name,last_name=last_name,username=username)
    user.set_password(password)
    user.save(using=self._db)
    return user
  
  def create_superuser(self,email,first_name,last_name,username,password):
    user=self.create_user(email=email,first_name=first_name,last_name=last_name,username=username,password=password)
    user.is_staff=True
    user.is_admin=True
    user.is_active=True
    user.is_superadmin=True
    user.save(using=self._db)
    return user

class Account(AbstractBaseUser):
  email=models.EmailField(unique=True)
  username=models.CharField(max_length=50,unique=True)
  first_name=models.CharField(max_length=50)
  last_name=models.CharField(max_length=50)
  phone_number=models.CharField(max_length=20,blank=True)

  date_joined=models.DateTimeField(auto_now_add=True)
  last_login=models.DateTimeField(auto_now=True)
  is_active=models.BooleanField(default=False)
  is_staff=models.BooleanField(default=False)
  is_admin=models.BooleanField(default=False)
  is_superadmin=models.BooleanField(default=False)

  USERNAME_FIELD='email'
  REQUIRED_FIELDS=['first_name','last_name','username']

  objects=AccountManager()

  def full_name(self):
    return f'{self.first_name} {self.last_name}'
  
  def __str__(self):
    return self.email
  
  def has_perm(self,perms,obj=None):
    return self.is_admin
  
  def has_module_perms(self,addlabel):
    return True

class UserProfile(models.Model):
  user=models.OneToOneField(Account,on_delete=models.CASCADE)
  profile_picture=CloudinaryField('image',blank=True)
  address_line_1=models.CharField(max_length=100,blank=True)
  address_line_2=models.CharField(max_length=100,blank=True)
  city=models.CharField(max_length=100,blank=True)
  state=models.CharField(max_length=100,blank=True)
  country=models.CharField(max_length=100,blank=True)

  def __str__(self):
    return self.user.first_name
  
  def full_address(self):
    return f'{self.address_line_1} {self.address_line_2}'

