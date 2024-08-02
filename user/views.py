import json

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest.views import verify_auth_token
from .forms import *
from helpers.dbhelper import DBOperation
from rest.register_views import Menu
from configuration import *
from user.register_views import Cart

@csrf_exempt
@verify_auth_token
@require_http_methods(["POST"])
def create_cart(request,*args,**kwargs):
    EVENT = "Create Cart for User"
    IP = client_ip(request)
    LOG_PREFIX = f'"EventName":"{EVENT}", "IP":"{IP}"'
    cls_menu = Menu()
    cls_ops_cart = DBOperation(COLLECTION_CART)
    cls_cart = Cart()
    log.info(LOG_PREFIX)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

        except json.JSONDecodeError:
            return JsonResponse({'status':"FAILURE","statuscode":'400',"msg":"Invalid Json"})

        form = CartForm(data)

        if form.is_valid():
            user_id = kwargs.get('unique_id')
            item_id = data.get('item_id')
            item_quantity = data.get('item_quantity')
            action = data.get('action')

            # Fetch item
            item = cls_menu._detail_item('LOG_PREFIX', item_id)
            log.info("ITEM DETAILS ::::: %s" % item)
            if not item:
                return JsonResponse({'status':'FAILURE','statuscode':404,'msg': 'Invalid Item Selected!'})

            # fetch cart
            cart = cls_ops_cart._find_one({'userid': user_id})

            if action == "add":
                response = cls_cart.add_to_cart('LOG_PREFIX ',cart,user_id,item,item_id,item_quantity)

            elif action == "remove":
                response = cls_cart.sub_from_cart('LOG_PREFIX ',cart,user_id,item, item_id, item_quantity)

            else:
                return JsonResponse({'status':'FAILURE','statuscode':'402','msg':'Invalid action'})

            return response

        return JsonResponse({'status': 'FAILURE', 'statuscode': '400', 'msg': form.errors})























