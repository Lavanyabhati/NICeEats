from django.contrib import admin
from django.urls import path, include
from .login import *

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', index),
    path('auth/', include('Auth.urls')),
    path('user/', include('user.urls')),
    path('restaurant/', include('rest.urls')),
    path('agent/', include('delivery.urls'))

]
