from django.urls import path
from .views import *
from Auth import views as authviews

urlpatterns = [
    path('otp/', authviews.otp, name='OTP'),
    path('add/', register_res, name='register_add'),
    path('update/', update_res, name='register_update_db'),
    path('owner/update/', update_res_owner, name='update_res_owner'),
    path('delete/', delete_res, name='register_delete'),


    path('details/', get_res, name='get_res'), #/restaurant/get_res_deatils/
    path('menu/add/', add_item, name='add_item'), #/restaurant/menu/add/
    path('menu/update/', update_item, name='update_item'), #/restaurant/menu/update/
    path('menu/delete/', delete_item, name='delete_item'), #/restaurant/menu/delete/
    path('menu/list/', list_item, name='list_item'), #/restaurant/menu/list/
    # path('menu/rate/', rate_item, name='rate_item'), #/restaurant/menu/rate/(average rating for item as well as restaurant to be returned)
    # path('menu/rate/update', update_rate_item, name='update_rate_item'), #/restaurant/menu/rate/(average rating for item as well as restaurant to be returned)
    path('list/', list_res, name='register_list'),

]
