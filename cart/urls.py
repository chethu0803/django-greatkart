from django.urls import path
from . import views
urlpatterns = [
    path('',views.cart,name="cart"),
    path('checkout/',views.checkout,name="checkout"),
    path('add_cart/<int:product_id>/',views.add_cart,name="add_cart"),
    path('remove/<int:product_id>/<int:cart_item_id>/',views.remove,name="remove"),
    path('remove_item/<int:product_id>/<int:cart_item_id>/',views.remove_item,name="remove_item"),
]
