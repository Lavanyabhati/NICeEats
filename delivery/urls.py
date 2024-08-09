from django.urls import path
from .views import *
from Auth import views as authviews

urlpatterns = [
    path('otp/', authviews.otp, name='OTP'),
    path('profile/update/', update_agent, name='update_agent'),
    path('session/', agent_session, name='agent_session'),
    # path('session/update/', update_session, name='update_session'),
    path('profile/status/', profile_status, name='profile_status'),
    path('location/', delivery_agent_location, name='delivery_agent_location'),
    path('location/update/', update_agent_location, name='update_agent_location'),
    path('order_status/update/', update_order_status, name='update_order_status'),
    path('profile/delete/', delete_agent, name='update_agent'),
    path('session/list/', sessions_list, name='list_sessions'),
]