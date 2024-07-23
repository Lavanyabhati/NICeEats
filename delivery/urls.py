from django.urls import path
from .views import *
from Auth import views as authviews

urlpatterns = [
    path('otp/', authviews.otp, name='OTP'),
#    path('profile/create/', register_agent, name='register_agent'),
    path('profile/update/', update_agent, name='update_agent'),
    path('profile/session/', agent_session, name='agent_session'),
    # path('profile/delete/', delete_agent, name='update_agent'),
    # path('session/create/', create_session, name='create_session'),
    # path('session/update/', update_session, name='update_session'),
    # path('session/list/', list_sessions, name='list_sessions'),
    ]
