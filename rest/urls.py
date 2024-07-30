from django.urls import path
from .views import *
from Auth import views as authviews

urlpatterns = [
    path('otp/', authviews.otp, name='OTP'),
    path('add/', register_res, name='register_add'),
    path('update/', update_res, name='register_update_db'),
    path('owner/update/', update_res_owner, name='update_res_owner'),
    path('delete/', delete_res, name='register_delete'),
    path('list/', list_res, name='register_list'),
    path('details/', get_res, name='get_res'),
    path('owner/details/', get_res_owner, name='get_res_owner'),
    path('menu/add/', add_item, name='add_item'),
    path('menu/update/', update_item, name='update_item'),
    path('menu/delete/', delete_item, name='delete_item'),
    path('menu/list/', list_item, name='list_item'),
    path('menu/rate/', item_rating, name='item_rating'),
    path('menu/rate/update/', update_rating, name='update_rating'),
]
