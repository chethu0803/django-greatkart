from django.urls import path
from . import views
urlpatterns = [
    path('',views.dashboard,name="dashboard"),
    path('register/',views.register,name="register"),
    path('login/',views.login,name="login"),
    path('logout/',views.logout,name="logout"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('forgotPassword/',views.forgotPassword,name="forgotPassword"),
    path('resetpassword-validate/<uidb64>/<token>/',views.resetPassword_validate,name="resetPassword_validate"),
    path('resetPassword/',views.resetPassword,name="resetPassword"),
    path('activate/<uidb64>/<token>/',views.activate,name="activate"),
    path('my-orders/',views.my_orders,name="my_orders"),
    path('edit-profile/',views.edit_profile,name="edit_profile"),
    path('change-password/',views.change_password,name="change_password"),
    path('order-detail/<int:order_id>/',views.order_detail,name="order_detail"),

]
