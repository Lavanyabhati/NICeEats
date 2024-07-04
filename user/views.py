from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from django.views.generic import TemplateView, FormView
from bson import ObjectId
from .register_views import Register
from django.contrib.auth.decorators import login_required
from .forms import *
from datetime import datetime
from configuration import *
from user.register_views import Register


def product_list(request):
    return HttpResponse('ok')


def order_list(request):
    return HttpResponse('return list of orders!')


def cart_list(request):
    return HttpResponse('return list of items in cart!')


# def register_user(request):
#     cls_register = Register()
#     try:
#         post_data = request.POST
#         form = UserForm(post_data)
#         if not form.is_valid():
#             return JsonResponse({"status": "FAILURE", "statuscode": 400, "msg": form.errors})
#     ## What to do here??
#     ## corresponding to a verified user, there will be a document
#     # containing the mobile number of the user. So, given the additional
#     # user data, I need to
#     # call the update function to add the remaining data for that user, and
#     # return a corresponding JSON response for it. (Include the three fields -
#     # {status, statuscode, msg}
#     # and lastly, handle exceptions.
#

