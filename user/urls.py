from django.urls import path
from . import views
from Auth import views as authviews

urlpatterns = [
    path('otp/', authviews.otp),
    path('product/', views.product_list),
    path('orders/', views.order_list),
    path('cart/', views.cart_list)
]
