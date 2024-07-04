from django.urls import path
from .views import *
from Auth import views as authviews

urlpatterns = [
    path('otp/', authviews.otp, name='OTP'),
    path('add/', register_res, name='register_add'),
    path('list/', list_res, name='register_list'),
    path('update/', update_res, name='register_update_db'),
    path('list/', delete_res, name='register_delete'),
    path('update/', register_res_owner, name='register_res_owner')

]
