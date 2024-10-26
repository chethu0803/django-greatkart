from django import forms
from .models import Account,UserProfile
from cloudinary.forms import CloudinaryFileField
class RegistrationForm(forms.ModelForm):
  password=forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder':"Enter Password",
    'class':'form-control'
  }))
  confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder':"Confirm password",
    'class':'form-control'
  }))
  class Meta:
    model=Account
    fields=['first_name','last_name','email','phone_number','password']

  def clean(self):
    cleaned_data=super(RegistrationForm,self).clean()
    password=cleaned_data.get('password')
    confirm_password=cleaned_data.get('confirm_password')

    if password!=confirm_password:
      raise forms.ValidationError("Password does not match")



  def __init__(self,*args,**kwargs):
    super(RegistrationForm,self).__init__(*args,**kwargs)
    self.fields['first_name'].widget.attrs['placeholder']='Enter First Name'
    self.fields['last_name'].widget.attrs['placeholder']='Enter Last Name'
    self.fields['email'].widget.attrs['placeholder']='Enter email address'
    self.fields['phone_number'].widget.attrs['placeholder']='Enter Phone Number'
    for field in self.fields:
      self.fields[field].widget.attrs['class']="form-control"


class UserForm(forms.ModelForm):
  class Meta:
    model=Account
    fields=['first_name','last_name','phone_number']

  def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
  profile_pic = CloudinaryFileField(
    widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    options={
      'folder': 'user_profiles',  # replace with your desired folder path
      'tags': 'user_picture',
      'format': 'png',
    },
    required=False 
  )

  class Meta:
    model=UserProfile
    fields=['address_line_1','address_line_2','city','state','country','profile_pic']
   

  def __init__(self, *args, **kwargs):
    super(UserProfileForm, self).__init__(*args, **kwargs)
    for field in self.fields:
      self.fields[field].widget.attrs['class'] = 'form-control'
      