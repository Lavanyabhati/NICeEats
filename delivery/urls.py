from django.urls import path
from .views import *
from Auth import views as authviews

urlpatterns = [
    path('otp/', authviews.otp, name='OTP'),
    path('profile/update/', update_agent, name='update_agent'),
    path('session/', agent_session, name='agent_session'),
    path('session/update/', update_session, name='update_session'),
    # path('profile/status', profile_status, name='profile_status'),
    # path('profile/location/', agent_location, name='agent_location'),
    # path('profile/delete/', delete_agent, name='update_agent'),
    # path('session/list/', list_sessions, name='list_sessions'),
    ]
