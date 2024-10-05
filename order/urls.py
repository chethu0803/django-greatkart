from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('place-order/',views.placeorder,name="placeorder"),
    path('payments/',views.payments,name="payments"),
]